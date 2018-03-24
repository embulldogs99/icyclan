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

)

type user struct {
  Email string
  Pass string
}

//creates global userid and sessionid hashtables
var dbu = map[string]user{} //user id, stores users
var dbs = map[string]string{} //session id, stores userids

func main() {

  //create 1 time use user variables
  var email string
  var pass string
  var balance float64
  var memberflag string
  //pulls users from database
  dbusers, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {log.Fatalf("Unable to connect to the database")}
  rowz, err := dbusers.Query("SELECT * FROM fmi.members")
  if err != nil {log.Fatalf("Could not Scan User Data")}
  //userslists:=user{}
  for rowz.Next(){
    //userslist:=user{}
    err:=rowz.Scan(&email, &pass,&balance,&memberflag)
    if err != nil {log.Fatal(err)}
    dbu[email]=user{email,pass}

  }

  dbusers.Close()


//Begin Serving the FIles

  s := &http.Server{
    Addr:    ":80",
    Handler: nil,
  }

  http.Handle("/favicon/", http.StripPrefix("/favicon/", http.FileServer(http.Dir("./favicon"))))
  http.Handle("/pics/", http.StripPrefix("/pics/", http.FileServer(http.Dir("./pics"))))
	http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("./css"))))
  http.Handle("/research/", http.StripPrefix("/research/", http.FileServer(http.Dir("./research"))))

  http.HandleFunc("/", serve)
  http.HandleFunc("/marketmentions", servemarketmentions)
  http.HandleFunc("/about", serveabout)
  http.HandleFunc("/contact", servecontact)
  http.HandleFunc("/researchlinks", researchlinks)
  http.HandleFunc("/research/roa", researchroa)
  http.HandleFunc("/research/eps", researcheps)
  http.HandleFunc("/signup", signup)
  http.HandleFunc("/login", login)
  http.HandleFunc("/logout", logout)
  http.HandleFunc("/profile", profile)
  http.HandleFunc("/investors", investors)
  log.Fatal(s.ListenAndServe())
}


type Newspoint struct {
	Target int
	Price  int
	Returns sql.NullFloat64
	Ticker sql.NullString
  Note sql.NullString
  Date sql.NullString
  Q_eps sql.NullFloat64
  A_eps sql.NullFloat64
  Report sql.NullString
}



type Member struct{
  Email sql.NullString
  Pass sql.NullString
  Balance sql.NullFloat64
  Memberflag sql.NullString
}

func membercheck(e string, p string) bool{
  dbusers, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {
    log.Fatalf("Unable to connect to the database")
  }
  u, err := dbusers.Exec(`SELECT * FROM fmi.members WHERE email=$1 AND pass=$2;`, e,p)
  if u == nil {
    dbusers.Close()
    return false
  } else {
  dbusers.Close()
  return true
}
}


func signup(w http.ResponseWriter, r *http.Request){
  if alreadyLoggedIn(r)==false{
    var tpl *template.Template
    tpl = template.Must(template.ParseFiles("signup.gohtml","css/main.css","css/mcleod-reset.css",))
    tpl.Execute(w, nil)
    if r.Method == http.MethodPost {
      email := r.FormValue("email")
      pass := r.FormValue("pass")
      if membercheck(email,pass) == true{
        profile(w,r)
      }else{
        dbusers, _ := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
        _, err := dbusers.Exec(`INSERT INTO fmi.members (email, pass, balance, memberflag ) VALUES ($1, $2, $3, $4);`, email, pass, 0, 'p')
        dbusers.Close()
        if err != nil {
          http.Redirect(w, r, "/login", http.StatusSeeOther)
      }
      fmt.Printf("Added User: "+email+" At Time : "+time.Now().Format("2006-01-02 15:04:05"))
      http.Redirect(w, r, "/profile", http.StatusSeeOther)
      }
    }
  }else{
    http.Redirect(w, r, "/profile", http.StatusSeeOther)
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
  if alreadyLoggedIn(r) {
    http.Redirect(w, r, "/profile", http.StatusSeeOther)
    return
  }

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
		if pass != u.Pass {
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
    http.Redirect(w, r, "/profile", http.StatusSeeOther)
    fmt.Printf(email + " logged on")

	}
  //html template
    var tpl *template.Template
    tpl = template.Must(template.ParseFiles("login.gohtml","css/main.css","css/mcleod-reset.css",))
    tpl.Execute(w, nil)
  }




func logout(w http.ResponseWriter, r *http.Request) {
	if !alreadyLoggedIn(r) {http.Redirect(w, r, "/login", http.StatusSeeOther)}
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





func profile(w http.ResponseWriter, r *http.Request){
    if !alreadyLoggedIn(r){http.Redirect(w, r, "/login", http.StatusSeeOther)}

    var email sql.NullString
    var pass sql.NullString
    var balance sql.NullFloat64
    var memberflag sql.NullString

    currentuser:=getUser(w,r)
    dbusers, _ := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
    _ = dbusers.QueryRow("SELECT * FROM fmi.members WHERE email=$1",currentuser.Email).Scan(&email, &pass, &balance, &memberflag)
    data:=Member{email, pass, balance, memberflag}

    dbusers.Close()
    var tpl *template.Template
    tpl = template.Must(template.ParseFiles("profile.gohtml","css/main.css","css/mcleod-reset.css"))

    tpl.Execute(w,data)
}











func dbpull1() []Newspoint {

  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {
    log.Fatalf("Unable to connect to the database")
  }

  sqlstatmt:="SELECT * FROM fmi.marketmentions WHERE report='analyst' AND date > current_timestamp - INTERVAL '1 day';"
  // fmt.Println(sqlstatmt)
  rows, err := db.Query(sqlstatmt)

  if err != nil{
    log.Fatalf("failed to select marketmentions data")
  }

  bks := []Newspoint{}
  for rows.Next() {
    bk := Newspoint{}
    err := rows.Scan(&bk.Target, &bk.Price, &bk.Returns, &bk.Ticker, &bk.Note, &bk.Date, &bk.Q_eps, &bk.A_eps, &bk.Report)

    if err != nil {
      log.Fatal(err)
    }
  	// appends the rows
    bks = append(bks, bk)
  }


  db.Close()
  return bks
}

func dbpull365() []Newspoint {

  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {
    log.Fatalf("Unable to connect to the database")
  }

  sqlstatmt:="SELECT * FROM fmi.marketmentions WHERE report='analyst' AND date > current_timestamp - INTERVAL '365 days';"
  // fmt.Println(sqlstatmt)
  rows, err := db.Query(sqlstatmt)

  if err != nil{
    log.Fatalf("failed to select marketmentions data")
  }

  bks := []Newspoint{}
  for rows.Next() {
    bk := Newspoint{}
    err := rows.Scan(&bk.Target, &bk.Price, &bk.Returns, &bk.Ticker, &bk.Note, &bk.Date, &bk.Q_eps, &bk.A_eps, &bk.Report)

    if err != nil {
      log.Fatal(err)
    }
  	// appends the rows
    bks = append(bks, bk)
  }


  db.Close()
  return bks
}




func serve(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("main.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, dbpull1())
}
func servemarketmentions(w http.ResponseWriter, r *http.Request){
  z:=getUser(w,r)
  if membercheck(z.Email,z.Pass) == true{
  tpl := template.Must(template.ParseFiles("marketmentions.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, dbpull365())
  }else{http.Redirect(w, r, "/", http.StatusSeeOther)}
}
func serveabout(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("about.gohtml","css/main.css","css/mcleod-reset.css" ))
  tpl.Execute(w, nil)
}
func servecontact(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("contact.gohtml","css/main.css","css/mcleod-reset.css" ))
  tpl.Execute(w, nil)
}
func researchlinks(w http.ResponseWriter, r *http.Request){
  if !alreadyLoggedIn(r){http.Redirect(w, r, "/login", http.StatusSeeOther)}
  tpl := template.Must(template.ParseFiles("researchlinks.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
func researchroa(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("research/roa.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
func investors(w http.ResponseWriter, r *http.Request){
  if !alreadyLoggedIn(r){http.Redirect(w, r, "/login", http.StatusSeeOther)}
  tpl := template.Must(template.ParseFiles("investors.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
func researcheps(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("research/eps.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
