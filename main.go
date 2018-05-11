package main
import(
  "net/http"
  	"html/template"
)

func main(){
  s:=&http.Server{
    Addr: ":80",
    Handler: nil,
  }

	http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("./css"))))
  http.HandleFunc("/", serve)

}

func serve(){
  tpl:=template.Must(template.ParseFiles("main.gohtml","css/main.css","css/mcleod-reset.css"))
  tpl.Execute(w, nil)
}
