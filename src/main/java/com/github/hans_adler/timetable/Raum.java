package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitCodename;

@Table(value="raeume")
public class Raum
extends Model
implements MitCodename {
    String getHaus() {
        return getString("haus");
    }
}
