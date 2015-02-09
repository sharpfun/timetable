package com.github.hans_adler.timetable.mixin;

public interface MitCodename
extends ModelInterface {
    public default String getCodename() {
        return getString("codename");
    }
}
