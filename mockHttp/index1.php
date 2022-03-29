<?php
	header("Content-Type: application/json");
	$payload = file_get_contents('php://input');
   $var = json_decode($payload,true);
   $var2 = implode("|",$var);

   $applicationID =$var['applicationID'];
   $applicationName =$var['applicationName'];
   $deviceName =$var['deviceName'];
   $devEUI =$var['devEUI'];
   $data64    = $var['data'];

   foreach($var['rxInfo'] as $value)
      {			 
	   $gatewayID =$value['gatewayID'];
	   $name =$value['name'];
	   $time =$value['time'];
	   $rssi =$value['rssi'];
	   $loRaSNR =$value['loRaSNR'];
    }
    var_dump($data64);
?>
