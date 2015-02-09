package com.github.hans_adler.timetable.mixin;

public interface MitKurzname extends MitName {
    
    public default String getKurzname() {
        return getString("kurzname");
    }

}
