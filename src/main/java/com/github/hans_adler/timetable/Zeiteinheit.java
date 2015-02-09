package com.github.hans_adler.timetable;

import java.sql.Time;
import java.util.Date;
import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import org.javalite.common.ConversionException;

@Table(value="zeiteinheiten")
public class Zeiteinheit extends Model {
    public Time getVon() {
        return convertToTime(get("von"));
    }
    public Time getBis() {
        return convertToTime(get("bis"));
    }
    private Time convertToTime(Object time) {
        if (time == null) return null;
        if (time instanceof Time) return (Time) time;
        if (time instanceof String) return Time.valueOf((String) time);
        if (time instanceof Long) return new Time((Long) time);
        if (time instanceof Date) return new Time(((Date) time).getTime());
        try {
            return Time.valueOf(time.toString());
        } catch (IllegalArgumentException e) {
            throw new ConversionException("failed to convert: '" + time + "' to java.sql.Time", e);
        }
    }
}
