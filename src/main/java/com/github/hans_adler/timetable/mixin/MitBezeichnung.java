package com.github.hans_adler.timetable.mixin;

public interface MitBezeichnung extends ModelInterface {
    
    public default String getBezeichnung() {
        return getString("bezeichnung");
    }

}
