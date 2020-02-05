<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

<style>
body {
  padding-top: 50px;
}
.spacer {
  margin-top: 2%;
  margin-bottom: 2%;
}
.block {
  height: 300px;
  padding-top: 15px;
  background-color: lightgray;
}
.block2 {
  min-height: 160px;
  padding-top: 15px;
}
.doalign {
  position: absolute;
/*  top: 0;
  bottom: 0; */
  left: 0;
  right: 0;
  margin: auto;
}
xmp{
    white-space:pre-line;
}
</style>

  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

</head>
<body>


        <div class="panel-group" id="accordion">

        <!-- NOTABLE THINGS -->
        <div class="panel panel-default">
           <div class="panel-heading">
                  <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#collapse1">
                  Notable Things</a>
                  </h4>
           </div>
           <div id="collapse1" class="panel-collapse collapse">
                  <div class="panel-body">
                  <xmp>
                  <?php
                  $narray = file("strace-notable.out");
                     foreach ( $narray as $line3 ) {
                         echo $line3;
                     }
                  echo "    ";
                  $tarray = file("curl-time.out");
                     foreach ( $tarray as $line4 ) {
                        echo $line4;
                     }
                  ?>
                  </xmp>
                  </div>
           </div>
        </div>

        <!-- ERRORS? -->
           <div class="panel panel-default">
                  <div class="panel-heading">
                  <h4 class="panel-title">
                         <a data-toggle="collapse" data-parent="#accordion" href="#collapse2">
                         Possible Errors</a>
                  </h4>
                  </div>
                  <div id="collapse2" class="panel-collapse collapse">
                         <div class="panel-body">

                  <xmp>
                  <?php
                  $earray = file("strace_errors.out");
                  foreach ( $earray as $line4 ) {
                         echo $line4;
                  }
                  ?>
                  </xmp>

                  </div>
           </div>
        </div>

        <!-- TOP 10 SLOW PATHS -->
        <div class="panel panel-default">
           <div class="panel-heading">
           <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#collapse3">
                  TOP 10 slowest paths</a>
                  </h4>
           </div>
           <div id="collapse3" class="panel-collapse collapse">
                  <div class="panel-body">

                  <?php
                  $parray = file("strace_paths_slow");
                  $reversedp = array_reverse($parray);
                  foreach ( $reversedp as $apath ) {
                            echo $apath . "<br/><br/>";
                  }
                  ?>

                  </div>
           </div>
        </div>


        <!-- TOP 10 SLOW QUERIES -->
        <div class="panel panel-default">
           <div class="panel-heading">
           <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#collapse4">
                  TOP 10 slowest queries</a>
                  </h4>
           </div>
           <div id="collapse4" class="panel-collapse collapse">
                  <div class="panel-body">

                  <?php
                  $sarray = file("strace_queries");
                  $reversed = array_reverse($sarray);
                  foreach ( $reversed as $aquery ) {
                            echo $aquery . "<br/><br/>";
                  }
                  ?>

                  </div>
           </div>
        </div>

        <!-- QUERY INFO -->
        <div class="panel panel-default">
           <div class="panel-heading">
           <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#collapse5">
                  Query info</a>
                  </h4>
           </div>
           <div id="collapse5" class="panel-collapse collapse">
                  <div class="panel-body">
                  Table mentions and count: possibly good for finding loops<BR>

                  <?php
                  $sarray = file("query_info");
                  $reversed = array_reverse($sarray);
                  foreach ( $reversed as $aquery ) {
                            echo $aquery . "<br/><br/>";
                  }
                  ?>

                  </div>
           </div>
        </div>

        <!-- REDIS ACTIVITY -->
        <div class="panel panel-default">
           <div class="panel-heading">
           <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#collapse6">
                  Redis activity</a>
                  </h4>
           </div>
           <div id="collapse6" class="panel-collapse collapse">
                  <div class="panel-body">
                  GREP for HMSET|HGET|HSET|HMGET|EXPIRE|redis<BR>
                  <xmp>
                <?php
                  $sarray = file("redis.out");
                  foreach ( $sarray as $aquery ) {
                            echo $aquery;
                  }
                  ?>
                  </xmp>
                  </div>
           </div>
        </div>

        <!-- RAW STRACE OUTPUT -->
        <div class="panel panel-default">
           <div class="panel-heading">
           <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#collapse7">
                  RAW strace output</a>
           </h4>
           </div>
           <div id="collapse7" class="panel-collapse collapse">
                  <div class="panel-body">
                  <xmp>
                  <?php
                  $sarray = file("strace.out");
                  foreach ( $sarray as $line2 ) {
                         echo $line2;
                  }
                  ?>
                  </xmp>
                  </div>
           </div>
        </div>

        </div>
        </body>

</html>
