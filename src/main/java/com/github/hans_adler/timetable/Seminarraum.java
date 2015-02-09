package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitKapazitaet;

@Table(value="seminarraeume")
public class Seminarraum
extends Model
implements MitKapazitaet {
    public Raum getRaum() {
        return Raum.findById(getId());
    }
}
