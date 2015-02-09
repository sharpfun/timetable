package app.controllers;

import org.javalite.activeweb.AppController;
import com.github.hans_adler.timetable.GeplanteLehrveranstaltung;
import com.github.hans_adler.timetable.Lehrveranstaltung;

public class LehrveranstaltungenController extends AppController {
    
    public void index() {
        view("lehrveranstaltungen", GeplanteLehrveranstaltung.findAll());
    }

}
