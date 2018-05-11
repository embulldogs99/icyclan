package main
import(
  "net/http"
  	"html/template"
    "log"
)

func main(){
  s:=&http.Server{
    Addr: ":80",
    Handler: nil,
  }

	http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("./css"))))
  http.HandleFunc("/", serve)
	log.Fatal(s.ListenAndServe())
}

func serve(w http.ResponseWriter, r *http.Request){
  tpl:=template.Must(template.ParseFiles("main.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
