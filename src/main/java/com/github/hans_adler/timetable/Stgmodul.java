package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitName;

@Table(value="stgmodule")
public class Stgmodul
extends Model
implements MitName {
    public Stg getStg() {
        return Stg.findById(get("stg"));
    }
}
