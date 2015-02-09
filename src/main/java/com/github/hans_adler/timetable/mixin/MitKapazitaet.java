package com.github.hans_adler.timetable.mixin;

public interface MitKapazitaet
extends ModelInterface {
    public default int getKapazitaet() {
        return getInteger("kapazitaet");
    }
}
