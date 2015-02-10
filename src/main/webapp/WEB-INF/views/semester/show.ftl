<h2>${semester}</h2>

<table cellpadding="5">

<tr>
	<th>&nbsp;</th>
    <th>Dauer</th>
    <th>Planungsperiode</th>
    <th>Vorlesungsperiode</th>
    <th>Einschreibeperiode</th>
    <th>Ausschreibeperiode</th>
</tr>

<tr>
    <th>von</th>
    <td>${semester.von}</td>
    <td>${semester.planungsbeginn}</td>
    <td>${semester.vorlesungsbeginn}</td>
    <td>${semester.einschreibebeginn}</td>
    <td>${semester.ausschreibebeginn}</td>
</tr>

<tr>
    <th>bis</th>
    <td>${semester.bis}</td>
    <td>${semester.planungsende}</td>
    <td>${semester.vorlesungsende}</td>
    <td>${semester.einschreibeende}</td>
    <td>${semester.ausschreibeende}</td>
</tr>

</table>

<h3>Geplante Lehrveranstaltungen</h3>

<table cellpadding="5">

<tr>
    <th>Bezeichnung</th>
    <th>Pflicht</th>
</tr>

<#list glvs as glv>
<tr>
    <td>${glv.lehrveranstaltung.bezeichnung}</td>
    <td>${glv.pflichtmodul}</td>
</tr>
</#list>

</table>

