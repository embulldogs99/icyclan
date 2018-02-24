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


func dbpull() []newspoint {

  db, err := sql.Open("postgres", "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable")
  if err != nil {
    log.Fatalf("Unable to connect to the database")
  }
  rows, _ := db.Query("SELECT * FROM fmi.marketmentions")
  bks := []newspoint{}
  for rows.Next() {
    bk := newspoint{}
    err := rows.Scan(&bk.target, &bk.price, &bk.return, &bk.ticker, &bk.note, &bk.date, &bk.q_eps, &bk.a_eps, &bk.report)
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
  dataset:=dbpull()
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
