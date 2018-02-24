package main
import(
  "net/http"
  	"html/template"
    "log"
    "database/sql"
_ "github.com/lib/pq"
)

func main() {

  s := &http.Server{
    Addr:    ":8080",
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
  log.Fatal(s.ListenAndServe())
}


type newspoint struct {
	Target int
	Price  int
	Return float32
	Ticker sql.NullString
  Note sql.NullString
  Date sql.NullString
  Q_eps float64
  A_eps float64
  Report sql.NullString
}


func dbpull(w http.ResponseWriter, r *http.Request) []newspoint {

  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {
    log.Fatalf("Unable to connect to the database")
  }

  rows, err := db.Query("SELECT * FROM fmi.marketmentions")
  bks := make([]newspoint, 0)
  for rows.Next() {
    bk := newspoint{}
    _ = rows.Scan(&bk.Target, &bk.Price, &bk.Return, &bk.Ticker, &bk.Note, &bk.Date, &bk.Q_eps, &bk.A_eps, &bk.Report)
		// appends the rows
    bks = append(bks, bk)
  }
  db.Close()
  return bks
}













func serve(w http.ResponseWriter, r *http.Request){
  tpl := template.Must(template.ParseFiles("main.gohtml","css/main.css","css/mcleod-reset.css"))
  dataset:=dbpull(w,r)
  tpl.Execute(w, dataset)
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
