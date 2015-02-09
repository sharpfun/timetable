package com.github.hans_adler.timetable.mixin;

public interface MitName extends ModelInterface {
    
    public default String getName() {
        return getString("name");
    }

}
