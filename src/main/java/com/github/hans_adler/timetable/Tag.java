package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitKurzname;

@Table(value="tage")
public class Tag
extends Model
implements MitKurzname {}
