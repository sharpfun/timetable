<h2>Alle Semester</h2>
<table cellpadding="5">

<tr>
    <th>Jahr</th>
    <th>Semester</th>
    <th>Geplante Lehrveranstaltungen</th>
</tr>

<#list semester as semester>
<tr>
    <td><a href="/semester/id?id=${semester.id}">${semester.jahr}</a></td>
    <td><a href="/semester/id?id=${semester.id}">${semester.bezeichnung}</a></td>
    <td>${semester.countAllGeplanteLehrveranstaltungen()}</td>
</tr>
</#list>

</table>

