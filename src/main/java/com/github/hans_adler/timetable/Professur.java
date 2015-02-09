package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitBezeichnung;

@Table(value="professuren")
public class Professur extends Model
implements MitBezeichnung {}
