%include('header',title='Monitor')
%include('navbar')
%include('navactions')

<div id="output" style="width:648px;height:200px;"></div>

<script language="Javascript" type="text/javascript">

showOutput = function(){
   update_interval = 1000;
   jQuery('#output').load('/{{app}}/{{cid}}/tail', function(){
      setTimeout(showOutput, update_interval);
   })
}

showOutput();

</script>

<!--
%if defined('jid'):
<form method="post" action="/proc/stop">
   <input type="hidden" name="cid" value="{{cid}}">
   <input type="hidden" name="app" value="{{app}}">
   <input type="hidden" name="jid" value="{{jid}}">
   <input type="submit" class="submit stop" value="stop">
</form>
%end
-->

