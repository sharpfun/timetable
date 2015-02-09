package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitBezeichnung;

@Table(value="lehrveranstaltungen")
public class Lehrveranstaltung extends Model
implements MitBezeichnung {
    public Lehrform getLehrform() {
        return Lehrform.findById("lehrform");
    }
}
