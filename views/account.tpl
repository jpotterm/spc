%include('header')
%include('navbar')

<h1>{{user}}'s account</h1>
<br>

<fieldset>
<legend>Change Password</legend>
<form method="POST" action="/account/change_password">
<table>
<tr><td>Old password:</td> <td><input class="form-control" type="password" name="opasswd"></td></tr>
<tr><td>New password:</td> <td><input class="form-control" type="password" name="npasswd1"></td></tr>
<tr><td>New password (again):</td> <td><input class="form-control" type="password" name="npasswd2"></td></tr>
</table>
<input class="btn btn-default" type="submit">
</form>
</fieldset>

<fieldset>
<legend>Upload data to account</legend>
<form action="/upload" method="post" enctype="multipart/form-data">
  <!-- Category: <input type="text" name="category" /> -->
  <font size="+1">Select a file:</font>
  <input type="file" name="upload" /><br>
  <input class="btn btn-default" type="submit" value="Upload"/>
</form>
</fieldset>

%include('footer')
