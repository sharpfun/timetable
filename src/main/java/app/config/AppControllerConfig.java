package app.config;

import org.javalite.activeweb.AbstractControllerConfig;
import org.javalite.activeweb.AppContext;
import org.javalite.activeweb.controller_filters.DBConnectionFilter;
import org.javalite.activeweb.controller_filters.TimingFilter;
import app.controllers.LehrveranstaltungenController;
import app.controllers.SemesterController;

public class AppControllerConfig extends AbstractControllerConfig {

    public void init(AppContext context) {
        addGlobalFilters(new TimingFilter());
        add(new DBConnectionFilter()).to(
                LehrveranstaltungenController.class, 
                SemesterController.class
        );
    }
}
