package com.github.hans_adler.timetable.mixin;

public interface MitKuerzel extends ModelInterface {
    
    public default String getKuerzel() {
        return getString("kuerzel");
    }

}
