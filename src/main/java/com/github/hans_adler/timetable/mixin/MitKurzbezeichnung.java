package com.github.hans_adler.timetable.mixin;

public interface MitKurzbezeichnung extends MitBezeichnung {

    public default String getKurzbezeichnung() {
        return getString("kurzbezeichnung");
    }
}
