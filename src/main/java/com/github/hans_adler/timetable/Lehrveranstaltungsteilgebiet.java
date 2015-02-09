package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitBezeichnung;

@Table("lehrveranstaltungsteilgebiete")
public class Lehrveranstaltungsteilgebiet extends Model
implements MitBezeichnung {}
