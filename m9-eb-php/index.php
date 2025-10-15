<?php
  echo "Hello from a PHP application running in Elastic Beanstalk!";
  
  $timestamp = $_SERVER['REQUEST_TIME'];
  echo '<br/>Request time: ' . date('Y/m/d H:i:s', $timestamp);
?>