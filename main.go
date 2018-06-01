package main
import(
  "net/http"
  	"html/template"
    "log"
    "database/sql"
_ "github.com/lib/pq"
  "time"
  "fmt"
    	"github.com/satori/go.uuid"
    _ "strconv"
    "strings"

)

//create User struct for cookie tracking
type user struct {
  Email string
  Password string
}

//creates global userid and sessionid hashtables
var dbu = map[string]user{} //user id, stores users
var dbs = map[string]string{} //session id, stores userids

func main() {

  //create user variables
  var email string
  var password string

  //pulls users from database
  dbusers, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {log.Fatalf("Unable to connect to the database")}
  rowz, err := dbusers.Query("SELECT DISTINCT email,password FROM icy.users")
  if err != nil {log.Fatalf("Could not Scan User Data")}
  //userslists:=user{}
  for rowz.Next(){
    //userslist:=user{}
    err:=rowz.Scan(&email, &password)
    if err != nil {log.Fatal(err)}
    dbu[email]=user{email,password}
  }

  dbusers.Close()



  s:=&http.Server{
    Addr: ":80",
    Handler: nil,
  }

	http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("./css"))))
  http.HandleFunc("/", serve)
  http.HandleFunc("/login", login)
  http.HandleFunc("/logout", logout)
  http.HandleFunc("/home", home)
  http.HandleFunc("/forums", forums)
  http.HandleFunc("/forumscontent", forumscontent)
  http.HandleFunc("/signup", signup)
  http.HandleFunc("/joinleaderboard", joinleaderboard)
  http.HandleFunc("/leaderboard", leaderboard)
	log.Fatal(s.ListenAndServe())
}



func signup(w http.ResponseWriter, r *http.Request){
  if r.Method == http.MethodPost {
    email := r.FormValue("email")
    password := r.FormValue("password")
    curdate:= time.Now().Format("2006-01-02")
    dbusers, _ := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
    _, err := dbusers.Exec(`INSERT INTO icy.users (email, password,date) VALUES ($1, $2, $3);`, email, password, curdate)
    dbusers.Close()

    dbu[email]=user{email,password}

    if err != nil {http.Redirect(w, r, "/login", http.StatusSeeOther)}
    fmt.Printf("Added User: "+email+" At Time : "+time.Now().Format("2006-01-02 15:04:05"))
    http.Redirect(w, r, "/login", http.StatusSeeOther)
    }

  var tpl *template.Template
  tpl = template.Must(template.ParseFiles("signup.gohtml","css/main.css","css/mcleod-reset.css",))
  tpl.Execute(w, nil)

}


func joinleaderboard(w http.ResponseWriter, r *http.Request){
  var tpl *template.Template
  tpl = template.Must(template.ParseFiles("joinleaderboard.gohtml","css/main.css","css/mcleod-reset.css",))
  tpl.Execute(w, nil)


  if r.Method == http.MethodPost {
    email := r.FormValue("email")
    epicusername := r.FormValue("epicusername")
    date:=time.Now().Format("2006-01-02 15:04:05")
    dbusers, _ := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
    _, err := dbusers.Exec(`INSERT INTO icy.leaderboard (date, email, epicusername) VALUES ($1, $2, $3);`, date, email, epicusername)
    dbusers.Close()
    if err != nil {http.Redirect(w, r, "/login", http.StatusSeeOther)}
    fmt.Printf("Added User: "+email+" To Leaderboards At Time : "+date)
    http.Redirect(w, r, "/leaderboard", http.StatusSeeOther)
    }
}




func alreadyLoggedIn(req *http.Request) bool {
	c, err := req.Cookie("session")
	if err != nil {
		return false
	}
  email := dbs[c.Value]
	_, ok := dbu[email]
	return ok
}

func login(w http.ResponseWriter, r *http.Request) {
	//if already logged in send to login
  if alreadyLoggedIn(r) {http.Redirect(w, r, "/home", http.StatusSeeOther)}
	//grab posted form information
	if r.Method == http.MethodPost {
		email := r.FormValue("email")
		pass := r.FormValue("pass")
		//defines u as dbu user info (email,pass) then matches form email with stored email
		u, ok := dbu[email]

		if !ok {
			http.Error(w, "Username and/or password not found", http.StatusForbidden)
			return
		}
		//pulls password from u and checks it with stored password
		if pass != u.Password {
			http.Error(w, "Username and/or password not found", http.StatusForbidden)
			return
		}
		//create new session (cookie) to identify user
		sID, _ := uuid.NewV4()
		c := &http.Cookie{
			Name:  "session",
			Value: sID.String(),
		}
		http.SetCookie(w, c)
		dbs[c.Value] = email
    http.Redirect(w, r, "/home", http.StatusSeeOther)
    fmt.Printf(email + " logged on")

	}
  //html template
    var tpl *template.Template
    tpl = template.Must(template.ParseFiles("login.gohtml","css/main.css","css/mcleod-reset.css",))
    tpl.Execute(w, nil)
  }




func logout(w http.ResponseWriter, r *http.Request) {
	c, _ := r.Cookie("session")
	//delete the session
	delete(dbs, c.Value)
	//remove the cookie
	c = &http.Cookie{
		Name:  "session",
		Value: "",
		//max avge value of less than 0 means delete the cookie now
		MaxAge: -1,
	}
  http.SetCookie(w, c)
	http.Redirect(w, r, "/login", http.StatusSeeOther)
}

func getUser(w http.ResponseWriter, r *http.Request) user {
	//gets cookie
	c, err := r.Cookie("session")
	if err != nil {
		sID, _ := uuid.NewV4()
		c = &http.Cookie{
			Name:  "session",
			Value: sID.String(),
		}
	}
	//sets max age of cookie (time available to be logged in) and creates a cookie
	const cookieLength int = 14400
	c.MaxAge = cookieLength
	http.SetCookie(w, c)

	//if user already exists, get user
	var u user
	if email, ok := dbs[c.Value]; ok {
		u = dbu[email]
	}
	return u

}


func serve(w http.ResponseWriter, r *http.Request){
  if !alreadyLoggedIn(r) {http.Redirect(w, r, "/login", http.StatusSeeOther)}
  http.Redirect(w, r, "/home", http.StatusSeeOther)
}

func home(w http.ResponseWriter, r *http.Request){
  if !alreadyLoggedIn(r) {http.Redirect(w, r, "/login", http.StatusSeeOther)}
  tpl:=template.Must(template.ParseFiles("home.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}


func leaderboard(w http.ResponseWriter, r *http.Request){
  if !alreadyLoggedIn(r) {http.Redirect(w, r, "/login", http.StatusSeeOther)}

  type Leaderboard struct{

    Epicusername sql.NullString
    Squadkills sql.NullFloat64
    Duokills sql.NullFloat64
    Solokills sql.NullFloat64
    Squadmatch sql.NullFloat64
    Duomatch sql.NullFloat64
    Solomatch sql.NullFloat64
    Totalkills sql.NullFloat64
    Totalmatch sql.NullFloat64
    Killspermatch sql.NullFloat64
    Rank sql.NullFloat64
  }

  //pull leaderboard table
  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {log.Fatalf("Unable to connect to leaderboard database")}
  rows, err := db.Query("SELECT DISTINCT epicusername,squadkills,duokills,solokills,squadmatch,duomatch,solomatch,totalkills,totalmatch,killspermatch,rank() over (order by killspermatch desc) as rank FROM icy.leaderboard ORDER BY killspermatch DESC;")
  if err != nil{log.Fatalf("failed to select leaderboard data")}
  leaderboard := []Leaderboard{}
  rank:=0
  for rows.Next() {
    rank=rank+1
    bk := Leaderboard{}
    err := rows.Scan(&bk.Epicusername,&bk.Squadkills,&bk.Duokills,&bk.Solokills,&bk.Squadmatch,&bk.Duomatch,&bk.Solomatch,&bk.Totalkills,&bk.Totalmatch,&bk.Killspermatch,&bk.Rank)
    if err != nil {log.Fatal(err)}
    leaderboard = append(leaderboard, bk)
  }
  db.Close()

  tpl:=template.Must(template.ParseFiles("leaderboard.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, leaderboard)
}



type Forums struct{
  Postdate sql.NullFloat64
  Postcount sql.NullFloat64
  Poster sql.NullString
  Title sql.NullString
  Contents sql.NullString
  Imagefilelocation sql.NullString
}



func forums(w http.ResponseWriter, r *http.Request){
  if !alreadyLoggedIn(r) {http.Redirect(w,r,"/login", http.StatusSeeOther)}


  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {log.Fatalf("Unable to connect to leaderboard database")}
  rows, err := db.Query("SELECT DISTINCT title FROM icy.forums;")
  if err != nil{log.Fatalf("failed to select distinct icy forums titles")}

  type Forumstitlelist struct{
    Forumstitle string
  }

  titlelist := []Forumstitlelist{}
  for rows.Next() {
    bk := Forumstitlelist{}
    err := rows.Scan(&bk.Forumstitle)
    if err != nil {log.Fatal(err)}
    titlelist = append(titlelist, bk)
  }
  db.Close()

  tpl:=template.Must(template.ParseFiles("forums.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, titlelist)



  if r.Method == http.MethodPost {
    //defines u as dbu user info (email,pass) then matches form email with stored email

    current_time := time.Now().Local()
    u:=getUser(w,r)
    posttitle := r.FormValue("Title")
    contents := r.FormValue("Contents")
    imagefilename := r.FormValue("Imagefilelocation")
    imagefilelocation:="./fourms/images/"+imagefilename+".jpg"

    db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
    if err != nil {log.Fatalf("Unable to connect to forums database")}


    var rowcount int
    err = db.QueryRow("SELECT Count(DISTINCT title) FROM icy.forums;").Scan(&rowcount)
    if err != nil {log.Fatal(err)}
    postcount:=rowcount+1

    fmt.Println(u)
    fmt.Println(posttitle)
    fmt.Println(contents)
    fmt.Println(postcount)
    fmt.Println(current_time.Format("2006-01-02"))
    _, err = db.Query("INSERT INTO icy.forums (postdate,postcount,poster,title,contents,imagefilelocation) values(%s,%s,%s,%s,%s,%s);",current_time.Format("2006-01-02"),postcount,u,posttitle,contents,imagefilelocation)
    if err != nil{log.Fatalf("failed to insert new forums post")}
    db.Close()
    http.Redirect(w,r,"/forumscontent"+posttitle,http.StatusSeeOther)

  }

  //
  //For Uploading files
  //
  // file, header, err:=r.FormFile()
  // if err !=nil{http.Error(w,err.Error(),http.StatusInternalServerError)
  // return}
  // defer file.Close()
  // fmt.Printf("file uploaded")
  // f, er :=os.CreateFile("./forums/images/"+header.Filename)
  // if er != nil{fmt.Println(er)
  // return}
  // defer f.Close()
  // io.Copy(f,file)

}



func forumscontent(w http.ResponseWriter, r *http.Request){
  url:=r.URL.Path
  s:="/forums/images/"
  title:=strings.SplitAfter(url,s)

  type Holder struct{
    Forumstitle []string
    Forumscontent []Forums
  }



  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {log.Fatalf("Unable to connect to leaderboard database")}

  rows, _ := db.Query("SELECT postdate,postcount,poster,title,contents,imagefilelocation icy.forums where title=%s;",title)
  if err != nil{log.Fatalf("failed to select leaderboard data")}

  content:= []Forums{}

  for rows.Next() {
    bk := Forums{}
    err := rows.Scan(&bk.Postdate,&bk.Postcount,&bk.Poster,&bk.Title,&bk.Contents,&bk.Imagefilelocation)
    if err != nil {log.Fatal(err)}
    content = append(content, bk)
  }
  db.Close()

  dataholder:=Holder{title,content}



  if !alreadyLoggedIn(r) {http.Redirect(w,r,"/login", http.StatusSeeOther)}
  tpl:=template.Must(template.ParseFiles("forumscontent.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, dataholder)
}










///
