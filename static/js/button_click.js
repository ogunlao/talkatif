$(document).ready(function(){

  $('.keyboard_return').click(function(){
      var data_content = $('.materialize-textarea').fieldSelection();
      text_content = "\n"+"\n";
      $('.materialize-textarea').fieldSelection(text_content);
  });

  $('.heading').click(function(){
      var data_content = $('.materialize-textarea').fieldSelection();
      var text_content = data_content.text;
      text_content = "####"+text_content;
      $('.materialize-textarea').fieldSelection(text_content);
  });

    $('.bold').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "**"+text_content+"**";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.italic').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "*"+text_content+"*";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.quote').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "\n> "+text_content+"\n\n";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.link').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "["+text_content+"]"+"(http://)";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.list_bulleted').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "\n* "+text_content+"\n";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.list_numbered').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "\n1. "+text_content+"\n";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.satisfied').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "\n\n`I totally agree`\n\n";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.neutral').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "\n\n`I don't know`\n\n";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.dissatisfied').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "\n\n`I do not agree`\n\n";
        $('.materialize-textarea').fieldSelection(text_content);
    });

    $('.add_a_photo').click(function(){
        var data_content = $('.materialize-textarea').fieldSelection();
        var text_content = data_content.text;
        text_content = "\n![alt_name](" + text_content + ")\n\n";
        $('.materialize-textarea').fieldSelection(text_content);

    });








});
