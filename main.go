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
  rowz, err := dbusers.Query("SELECT email,password FROM icy.users")
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
  http.HandleFunc("/logout", login)
  http.HandleFunc("/home", home)
  http.HandleFunc("/signup", signup)
  http.HandleFunc("/joinleaderboard", joinleaderboard)
  http.HandleFunc("/leaderboard", leaderboard)
	log.Fatal(s.ListenAndServe())
}



func signup(w http.ResponseWriter, r *http.Request){
  var tpl *template.Template
  tpl = template.Must(template.ParseFiles("signup.gohtml","css/main.css","css/mcleod-reset.css",))
  tpl.Execute(w, nil)


  if r.Method == http.MethodPost {
    email := r.FormValue("email")
    password := r.FormValue("password")
    dbusers, _ := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
    _, err := dbusers.Exec(`INSERT INTO icy.users (email, password) VALUES ($1, $2);`, email, password)
    dbusers.Close()
    if err != nil {http.Redirect(w, r, "/login", http.StatusSeeOther)}
    fmt.Printf("Added User: "+email+" At Time : "+time.Now().Format("2006-01-02 15:04:05"))
    http.Redirect(w, r, "/home", http.StatusSeeOther)
    }
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
  }

  //pull leaderboard table
  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {log.Fatalf("Unable to connect to leaderboard database")}
  rows, err := db.Query("SELECT DISTINCT epicusername FROM icy.leaderboard;")
  if err != nil{log.Fatalf("failed to select leaderboard data")}
  leaderboard := []Leaderboard{}
  for rows.Next() {
    bk := Leaderboard{}
    err := rows.Scan(&bk.Epicusername)
    if err != nil {log.Fatal(err)}
    leaderboard = append(leaderboard, bk)
  }
  db.Close()

  tpl:=template.Must(template.ParseFiles("leaderboard.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, leaderboard)
}















///
