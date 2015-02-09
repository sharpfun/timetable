package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitKuerzel;
import com.github.hans_adler.timetable.mixin.MitName;

@Table(value="stg")
public class Stg
extends Model
implements MitName, MitKuerzel {}
