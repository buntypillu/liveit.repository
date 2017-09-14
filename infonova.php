<?php

$url = "";

if(isset($_REQUEST['url']))
{
	$url = $_REQUEST["url"];
}

$username = "";

if(isset($_REQUEST['username']))
{
	$username = $_REQUEST["username"];
}

$password = "";

if(isset($_REQUEST['password']))
{
	$password = $_REQUEST["password"];
}

$type = "";

if(isset($_REQUEST['type']))
{
	$type = $_REQUEST["type"];
}

$output = "";

if(isset($_REQUEST['output']))
{
	$output = $_REQUEST["output"];
}

$epg_shift = "";

if(isset($_REQUEST['epg_shift']))
{
	$epg_shift = $_REQUEST["epg_shift"];
}

if($url == "" || $username == "" || $password == "" || $type == "" || $output == "" || $epg_shift == "")
{
	echo("Preencha todos os campos necessários.");
}
else
{
	$file = $url."get.php?username=".$username."&password=".$password."&type=".$type."&output=".$output;
	$fileEPG = '#EXTM3U url-tvg="'.$url."xmltv.php?username=".$username."&password=".$password."&epg_shift=".$epg_shift.'"';
	
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, $file);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($ch, CURLOPT_SSLVERSION,3);
	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER,false);
	$data = curl_exec ($ch);
	curl_close ($ch);
	
	$destination = "./live.m3u";
	$f = fopen($destination, "w+");
	
	$newdata = str_replace("#EXTM3U", $fileEPG, $data);

	header('Content-Description: File Transfer'); 
	header('Content-Type: application/octet-stream'); 
	header('Content-Disposition: attachment; filename=live2.m3u'); 
	header('Content-Transfer-Encoding: binary'); 
	header('Expires: 0'); 
	header('Cache-Control: must-revalidate, post-check=0, pre-check=0'); 
	header('Pragma: public'); 
	header('Content-Length: ' . filesize($newdata)); 
	ob_clean(); 
		flush(); 
			readfile($newdata); 
		exit;
}

?>