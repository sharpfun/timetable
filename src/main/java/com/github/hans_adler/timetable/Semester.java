package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitKurzbezeichnung;
import com.github.hans_adler.timetable.mixin.MitCodename;

@Table(value="semester")
public class Semester
extends Model
implements MitKurzbezeichnung, MitCodename {
    public int getJahr() {
        return getInteger("jahr");
    }
    public Semester getVorgaenger() {
        return Semester.findById(get("vorgaenger"));
    }
}
