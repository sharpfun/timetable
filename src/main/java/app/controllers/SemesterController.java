package app.controllers;

import org.javalite.activeweb.AppController;
import org.javalite.activeweb.annotations.RESTful;
import com.github.hans_adler.timetable.Semester;

@RESTful
public class SemesterController extends AppController {
    
    public void index() {
        view("semester", Semester.findAll());
    }
    
    public void show() {
        Semester semester = Semester.findById(getId());
        view("semester", semester);
        view("glvs", semester.getAllGeplanteLehrveranstaltungen());
    }

    public void newForm(){}
    public void create(){}
    public void destroy(){}
    public void update(){}
    public void editForm(){}
}
