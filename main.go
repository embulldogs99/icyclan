package main
import(
  "net/http"
  	"html/template"
    "log"
    "database/sql"
_ "github.com/lib/pq"
  "time"
)

func main() {

  s := &http.Server{
    Addr:    ":80",
    Handler: nil,
  }

  http.Handle("/favicon/", http.StripPrefix("/favicon/", http.FileServer(http.Dir("./favicon"))))
  http.Handle("/pics/", http.StripPrefix("/pics/", http.FileServer(http.Dir("./pics"))))
	http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("./css"))))
  http.Handle("/research/", http.StripPrefix("/research/", http.FileServer(http.Dir("./research"))))

  http.HandleFunc("/", serve)
  http.HandleFunc("/about", serveabout)
  http.HandleFunc("/contact", servecontact)
  http.HandleFunc("/researchlinks", researchlinks)
  http.HandleFunc("/research/roa", researchroa)
  http.HandleFunc("/research/eps", researcheps)
  http.HandleFunc("/signup", signup)
  http.HandleFunc("/profile", profile)
  log.Fatal(s.ListenAndServe())
}


type newspoint struct {
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
  Email NullString
  Pass NullString
  Balance NullFloat64
  Memberflag NullString
}

func membercheck(e string, p string) bool{
  emailcheck = r.FormValue("email")
  passcheck = r.FormValue("pass")
  dbusers, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {
    log.Fatalf("Unable to connect to the database")
  }
  u, err = dbusers.Exec(`SELECT * FROM fmi.members WHERE email=$1 AND pass=$2;`, e,p)
  if u == nil {
    dbusers.Close()
    return false
  } else {
  dbusers.Close()
  return true
}
}


func signup(w http.ResponseWriter, r *http.Request) bool{
  if r.Method == http.MethodPost {
    email := r.FormValue("email")
    pass := r.FormValue("pass")
    if membercheck(email,pass) == true{
      profile(w,r)
    }else{
      _, err = dbusers.Exec(`INSERT INTO fmi.members (email, pass, balance, memberflag ) VALUES ($1, $2, $3, $4);`, email, pass, 0, 'p')
      if err != nil {
        http.Redirect(w, r, "/login", http.StatusSeeOther)
    }
    fmt.Printf("Added User: "+str(email)+" At Time : "+str(Now()))
    http.Redirect(w, r, "/profile", http.StatusSeeOther)
    }
  }
  var tpl *template.Template
  tpl = template.Must(template.ParseFiles("signup.gohtml","css/main.css","css/mcleod-reset.css",))
  tpl.Execute(w, nil)
}





func profile(w http.ResponseWriter, r *http.Request){
  if r.Method == http.MethodPost {
    emailcheck := r.FormValue("email")
    passcheck := r.FormValue("pass")
    if membercheck(emailcheck,passcheck)==false{
        http.Redirect(w, r, "/signup", http.StatusSeeOther)
    }else{
    var email NullString
    var pass NullString
    var balance NullFloat64
    var memberflag NullString


    dbusers, _ := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
    _ = dbusers.QueryRow("SELECT * FROM fmi.members WHERE email=$1 AND pass=$2",emailcheck,passcheck).Scan(&email, &pass, &balance, &memberflag)
    data:=Data{email, pass, balance}
    fmt.Println(email + " logged on")
    var tpl *template.Template
    tpl = template.Must(template.ParseFiles("profile.gohtml","css/main.css","css/mcleod-reset.css"))

    tpl.Execute(w,data)
      }
      }
}















func dbpull() []newspoint {

  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {
    log.Fatalf("Unable to connect to the database")
  }


  rows, _ := db.Query("SELECT * FROM fmi.marketmentions WHERE report='analyst' AND date > current_timestamp - interval '2 day'")
  bks := []newspoint{}
  for rows.Next() {
    bk := newspoint{}
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
  tpl.Execute(w, dbpull())
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
  tpl := template.Must(template.ParseFiles("researchlinks.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
func researchroa(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("research/roa.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
func researcheps(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("research/eps.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
