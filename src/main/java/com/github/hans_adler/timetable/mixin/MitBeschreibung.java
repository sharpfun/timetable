package com.github.hans_adler.timetable.mixin;

public interface MitBeschreibung extends ModelInterface {
    
    public default String getBeschreibung() {
        return getString("beschreibung");
    }

}
