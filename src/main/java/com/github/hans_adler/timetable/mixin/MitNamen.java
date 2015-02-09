package com.github.hans_adler.timetable.mixin;

public interface MitNamen extends ModelInterface {
    
    public default String getVorname() {
        return getString("vorname");
    }
    public default String getNachname() {
        return getString("nachname");
    }
    public default String getName() {
        return getVorname() + " " + getNachname();
    }

}
