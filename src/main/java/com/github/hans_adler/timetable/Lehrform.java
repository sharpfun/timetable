package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitKurzbezeichnung;

@Table(value="lehrformen")
public class Lehrform extends Model
implements MitKurzbezeichnung {
    public String getCodename() {
        return getString("codename");
    }
}
