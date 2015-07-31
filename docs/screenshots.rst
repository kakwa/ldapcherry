Screenshots
===========

.. raw:: html

    <style>
    #images {
      width: 800px;
      height: 600px;
      overflow: hidden;
      position: relative;
      
      margin: 20px auto;
    }
    #images img {
      width: 800px;
      height: 600px;
      
      position: absolute;
      top: 0;
      left: -400px;
      z-index: 1;
      opacity: 0;
      
      transition: all linear 500ms;
      -o-transition: all linear 500ms;
      -moz-transition: all linear 500ms;
      -webkit-transition: all linear 500ms;
    }
    #images img:target {
      left: 0;
      z-index: 9;
      opacity: 1;
    }
    #images img:first-child {
      left: 0;
      opacity: 1;
    }
    #slider {
      text-align: center;
    }
    #slider a {
      text-decoration: none;
      background: #E3F1FA;
      border: 1px solid #C6E4F2;
      padding: 4px 6px;
      color: #222;
      margin: 20px auto;
    }
    #slider a:hover {
        background: #C6E4F2;
    }
    </style>
    <div id="images">
        <img id="image1" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093051_1438x1064_scrot.png' />
        <img id="image2" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093130_1438x1064_scrot.png' />
        <img id="image3" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093147_1438x1064_scrot.png' />
        <img id="image4" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093152_1438x1064_scrot.png' />
        <img id="image5" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093215_1438x1064_scrot.png' />
        <img id="image6" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093234_1438x1064_scrot.png' />
    </div>
    <div id="slider">
        <a href="#image1">1</a>
        <a href="#image2">2</a>
        <a href="#image3">3</a>
        <a href="#image4">4</a>
        <a href="#image5">5</a>
        <a href="#image6">6</a>
    </div>
