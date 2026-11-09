package org.libsdl.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.graphics.*;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Toast;

public final class GameSettingsActivity extends Activity {
  private SharedPreferences prefs;
  private LauncherView launcher;
  private final String[] tabs={"Gráficos","Desempenho","Controles","Áudio"};
  private int tab=0;
  private int page=1;
  private int red=Color.rgb(255,18,34), white=Color.WHITE;
  private int muted=Color.rgb(190,198,210);
  private int bg=Color.rgb(5,6,9);
  private int dp(float v){return (int)(v*getResources().getDisplayMetrics().density+.5f);}
  @Override public void onCreate(Bundle b){
    super.onCreate(b);
    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
    getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_LAYOUT_STABLE|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    prefs=getSharedPreferences("recvx_settings",MODE_PRIVATE);
    launcher=new LauncherView(); setContentView(launcher);
  }
  private void choose(String title,String key,String[] values,int def){
    int selected=prefs.getInt(key,def);
    new AlertDialog.Builder(this).setTitle(title).setSingleChoiceItems(values,selected,(d,w)->{prefs.edit().putInt(key,w).apply();d.dismiss();launcher.invalidate();}).setNegativeButton("Cancelar",null).show();
  }
  private void toggle(String key,boolean def){prefs.edit().putBoolean(key,!prefs.getBoolean(key,def)).apply();launcher.invalidate();}
  private void message(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}

  private final class LauncherView extends View {
    Canvas c; Paint p=new Paint(3); Bitmap art; float sx,sy,downX,downY; boolean moved;
    LauncherView(){
      super(GameSettingsActivity.this);
      int id=getResources().getIdentifier("recvx_cover","drawable",getPackageName());
      if(id!=0) try{art=BitmapFactory.decodeResource(getResources(),id);}catch(Exception ignored){}
      setLayerType(View.LAYER_TYPE_SOFTWARE,null);
    }
    void paint(int color){p.setColor(color);p.setStyle(Paint.Style.FILL);p.setShader(null);p.clearShadowLayer();}
    void rect(float x,float y,float w,float h,int color,float r,int stroke){
      paint(color); c.drawRoundRect(x,y,x+w,y+h,r,r,p);
      if(stroke!=0){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.5f);p.setColor(red);c.drawRoundRect(x,y,x+w,y+h,r,r,p);p.setStyle(Paint.Style.FILL);}
    }
    void text(String s,float x,float y,float size,int color,boolean bold){
      paint(color);p.setTextSize(size);p.setTypeface(bold?Typeface.create("sans-serif",Typeface.BOLD):Typeface.create("sans-serif",Typeface.NORMAL));p.setTextAlign(Paint.Align.LEFT);c.drawText(s,x,y,p);
    }
    void center(String s,float x,float y,float size,int color,boolean bold){
      paint(color);p.setTextSize(size);p.setTypeface(bold?Typeface.create("sans-serif",Typeface.BOLD):Typeface.create("sans-serif",Typeface.NORMAL));p.setTextAlign(Paint.Align.CENTER);c.drawText(s,x,y,p);
    }
    void panel(float x,float y,float w,float h,String title){
      rect(x,y,w,h,0xE908090D,18,1);
      text(title,x+22,y+43,30,white,true);
    }
    void button(float x,float y,float w,float h,String label,boolean active){
      rect(x,y,w,h,active?0xFFB90013:0xF5111218,14,1);
      if(active){paint(0xFFFF2438);p.setShader(new LinearGradient(x,y,x,y+h,0xFFFF2538,0xFF8E000B,Shader.TileMode.CLAMP));c.drawRoundRect(x,y,x+w,y+h,14,14,p);p.setShader(null);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.5f);p.setColor(red);c.drawRoundRect(x,y,x+w,y+h,14,14,p);p.setStyle(Paint.Style.FILL);}
      center(label,x+w/2,y+h/2+8,active?24:22,white,true);
    }
    String val(String key,String[] opts,int def){int n=prefs.getInt(key,def);return opts[Math.max(0,Math.min(n,opts.length-1))];}
    void selectRow(float x,float y,float w,String label,String value){
      text(label,x,y+25,20,white,false);rect(x+w-330,y-8,320,48,0xFF202126,10,1);text(value,x+w-306,y+23,19,white,false);text("▼",x+w-45,y+22,16,red,true);
    }
    void switchRow(float x,float y,float w,String label,String key,boolean def){
      text(label,x,y+25,20,white,false);boolean on=prefs.getBoolean(key,def);
      rect(x+w-75,y-2,62,32,on?0xFFED1528:0xFF484B52,18,0);
      paint(white);c.drawCircle(x+w-(on?28:60),y+14,12,p);
    }
    void sliderRow(float x,float y,float w,String label,String key,int def){
      text(label,x,y+25,20,white,false);int v=prefs.getInt(key,def);
      paint(0xFF5D6066);c.drawRoundRect(x+w-340,y+5,x+w-55,y+17,8,8,p);
      paint(0xFFFF182B);c.drawRoundRect(x+w-340,y+5,x+w-340+285*v/100f,y+17,8,8,p);
      paint(white);c.drawCircle(x+w-340+285*v/100f,y+11,10,p);text(v+"%",x+w-45,y+24,18,white,true);
    }
    @Override protected void onDraw(Canvas canvas){
      super.onDraw(canvas);c=canvas;sx=getWidth()/1536f;sy=getHeight()/864f;c.save();c.scale(sx,sy);
      if(art!=null){paint(white);p.setFilterBitmap(true);c.drawBitmap(art,null,new Rect(0,0,1536,864),p);paint(0x55000000);c.drawRect(0,0,1536,864,p);}else{paint(bg);c.drawRect(0,0,1536,864,p);}
      // Side navigation and game branding
      rect(38,16,350,744,0xE90A0B10,24,1);
      center("RESIDENT EVIL",213,85,27,white,true);center("CODE: VERONICA X",213,119,27,white,true);center("HD",213,153,27,white,true);
      String[] menu={"▷  Iniciar Jogo","⚙  Configurações","♧  Controles","▣  Salvar / Carregar","ⓘ  Informações","⏻  Sair"};
      for(int i=0;i<menu.length;i++)button(54,178+i*91,318,78,menu[i],i==(page==0?0:1));
      // Main title and tabs
      text(page==0?"Iniciar Jogo":"Configurações",414,67,42,white,true);
      String[] icons={"▣  Gráficos","◉  Desempenho","♧  Controles","◖  Áudio"};
      for(int i=0;i<4;i++)button(410+i*278,92,266,80,icons[i],i==tab);
      if(page==0){
        panel(410,190,1090,460,"Iniciar Jogo");
        text("DIRETÓRIO DO JOGO: "+(prefs.getString("game_root","").isEmpty()?"Não selecionado":"Selecionado"),440,285,25,white,true);
        text("Use SELECIONAR PASTA DO JOGO na tela inicial para escolher Default.xex.",440,340,21,muted,false);
      }else if(tab==0){
        panel(410,190,675,480,"Gráficos");panel(1098,190,402,480,"Desempenho");
        String[] res={"720p (1280×720)","1080p (1920×1080)"};
        String[] scale={"100% (Nativa)","75%","50%"},quality={"Alta","Média","Baixa"},filter={"Bilinear","Nearest"};
        String[] fsr={"Desativado","FSR (FidelityFX)"},mode={"Quality (Melhor qualidade)","Balanced","Performance"};
        String[] aa={"Desativado","Ativado"},particles={"Alto","Médio","Baixo"},aspect={"Automática (16:9)","4:3","16:9","16:10"};
        String[] labels={"Resolução de saída","Escala de renderização","Qualidade de imagem","Filtro de imagem","Filtro FSR","Modo FSR","Nitidez (CAS)","Anti-aliasing (AA)","Efeitos de partículas","Proporção da tela"};
        String[] keys={"resolution","render_scale","image_quality","image_filter","fsr","fsr_mode","cas_sharpness","anti_aliasing","particles","aspect_ratio"};
        String[][] opts={res,scale,quality,filter,fsr,mode,null,aa,particles,aspect};
        int[] defs={1,0,0,0,0,0,70,0,0,0};
        for(int i=0;i<labels.length;i++){float yy=248+i*42;if(i==6)sliderRow(438,yy,620,labels[i],keys[i],70);else selectRow(438,yy,620,labels[i],val(keys[i],opts[i],defs[i]));}
        selectRow(1120,248,350,"Limite de FPS",val("fps_limit",new String[]{"30 FPS","60 FPS","120 FPS","Ilimitado"},1));
        switchRow(1120,294,350,"Sincronização vertical (V-Sync)","vsync",true);
        switchRow(1120,340,350,"Contador de FPS","show_fps",true);
        switchRow(1120,386,350,"Cache de shaders","shader_cache",true);
        switchRow(1120,432,350,"Reduzir efeitos pesados","reduce_effects",false);
        rect(1110,500,370,150,0xD91A1B20,12,1);
        text("ⓘ  Melhora a qualidade da imagem",1130,540,18,muted,false);text("com upscaling e nitidez (FSR/CAS),",1130,570,18,muted,false);text("com equilíbrio entre qualidade e",1130,600,18,muted,false);text("desempenho.",1130,630,18,muted,false);
      }else if(tab==1){
        panel(410,190,675,480,"Desempenho");panel(1098,190,402,480,"Informações");
        selectRow(438,255,620,"Limite de FPS",val("fps_limit",new String[]{"30 FPS","60 FPS","120 FPS","Ilimitado"},1));
        switchRow(438,320,620,"Sincronização vertical (V-Sync)","vsync",true);
        switchRow(438,380,620,"Contador de FPS","show_fps",true);
        switchRow(438,440,620,"Cache de shaders","shader_cache",true);
        switchRow(438,500,620,"Reduzir efeitos pesados","reduce_effects",false);
        text("O contador apresenta a taxa de",1120,270,18,muted,false);text("apresentação medida pelo renderer.",1120,300,18,muted,false);
        text("As opções ainda dependem de",1120,355,18,muted,false);text("integração real no runtime.",1120,385,18,muted,false);
      }else if(tab==2){
        panel(410,190,1090,480,"Controles");
        selectRow(440,270,1020,"Controles na tela",val("touch_mode",new String[]{"Automático","Sempre mostrar","Sempre ocultar"},0));
        button(440,340,1020,78,"↔  Editar posição dos controles",true);
        text("O editor permite arrastar o joystick e os botões.",450,470,20,muted,false);
        text("Ajustes de tamanho e transparência ainda não estão disponíveis.",450,510,20,muted,false);
        text("O modo automático deve ocultar os controles após entrada física confirmada.",450,560,20,muted,false);
      }else{
        panel(410,190,1090,480,"Áudio");
        sliderRow(440,280,1020,"Volume geral","audio_master",100);
        sliderRow(440,370,1020,"Volume da música","audio_music",100);
        sliderRow(440,460,1020,"Volume dos efeitos","audio_sfx",100);
        text("Os volumes são armazenados, mas ainda não estão conectados ao mixer.",450,570,19,muted,false);
      }
      button(410,692,520,68,"↶  Restaurar padrões",false);
      button(940,692,560,68,"✓  Aplicar",true);
      rect(38,778,1462,70,0xF008090D,10,1);
      text("▱  Diretório do jogo: Não selecionado",62,820,18,muted,false);
      text("♧  Controle: Desconectado",650,820,18,muted,false);
      text("♧  Controles na tela: Ativado",1010,820,18,0xFF35E66B,false);
      text("Versão: v1.0.0",1370,820,18,white,false);
      c.restore();
    }
    @Override public boolean onTouchEvent(MotionEvent e){
      float x=e.getX()/sx,y=e.getY()/sy;
      if(e.getAction()==MotionEvent.ACTION_DOWN){downX=x;downY=y;moved=false;return true;}
      if(e.getAction()==MotionEvent.ACTION_MOVE){if(Math.abs(x-downX)>15||Math.abs(y-downY)>15)moved=true;return true;}
      if(e.getAction()==MotionEvent.ACTION_UP&&!moved){handle(x,y);performClick();return true;}
      return true;
    }
    @Override public boolean performClick(){super.performClick();return true;}
    void handle(float x,float y){
      if(y>=92&&y<=172&&x>=410){tab=Math.max(0,Math.min(3,(int)((x-410)/278)));invalidate();return;}
      if(x>=38&&x<=388&&y>=178&&y<=720){
        int item=(int)((y-178)/91);
        if(item==0){finish();return;} if(item==1){page=1;invalidate();return;}
        if(item==2){tab=2;page=1;invalidate();return;}
        if(item==3){message("Salvar/carregar ainda não integrado ao runtime.");return;}
        if(item==4){new AlertDialog.Builder(GameSettingsActivity.this).setTitle("Informações").setMessage("Resident Evil Code: Veronica X HD — edição dublada para Android ARM64.").setPositiveButton("OK",null).show();return;}
        if(item==5){finish();return;}
      }
      if(y>=692&&y<=765&&x>=410&&x<930){prefs.edit().clear().apply();invalidate();message("Padrões restaurados.");return;}
      if(y>=692&&y<=765&&x>=940){prefs.edit().apply();message("Configurações salvas.");return;}
      if(tab==0){
        if(x>=740&&x<=1080&&y>=230&&y<670){
          int i=(int)((y-240)/42);String[] keys={"resolution","render_scale","image_quality","image_filter","fsr","fsr_mode","cas_sharpness","anti_aliasing","particles","aspect_ratio"};
          String[][] opts={{"720p (1280×720)","1080p (1920×1080)"},{"100% (Nativa)","75%","50%"},{"Alta","Média","Baixa"},{"Bilinear","Nearest"},{"Desativado","FSR (FidelityFX)"},{"Quality (Melhor qualidade)","Balanced","Performance"},null,{"Desativado","Ativado"},{"Alto","Médio","Baixo"},{"Automática (16:9)","4:3","16:9","16:10"}};
          if(i==6){int v=prefs.getInt("cas_sharpness",70);prefs.edit().putInt(keys[i],Math.min(100,v+10)).apply();invalidate();return;}
          if(i>=0&&i<keys.length)choose(keys[i],keys[i],opts[i],0);
          return;
        }
        if(x>1090&&y>230&&y<480){if(y<285)choose("Limite de FPS","fps_limit",new String[]{"30 FPS","60 FPS","120 FPS","Ilimitado"},1);else if(y<330)toggle("vsync",true);else if(y<375)toggle("show_fps",true);else if(y<420)toggle("shader_cache",true);else toggle("reduce_effects",false);invalidate();return;}
      }else if(tab==1&&x>430&&x<1080){if(y<300)choose("Limite de FPS","fps_limit",new String[]{"30 FPS","60 FPS","120 FPS","Ilimitado"},1);else if(y<365)toggle("vsync",true);else if(y<425)toggle("show_fps",true);else if(y<485)toggle("shader_cache",true);else toggle("reduce_effects",false);invalidate();return;}
      else if(tab==2){if(y>245&&y<320)choose("Controles na tela","touch_mode",new String[]{"Automático","Sempre mostrar","Sempre ocultar"},0);else if(y>330&&y<430)startActivity(new Intent(GameSettingsActivity.this,TouchLayoutEditorActivity.class));invalidate();return;}
      else if(tab==3&&y>240&&y<520){String[] keys={"audio_master","audio_music","audio_sfx"};int i=Math.max(0,Math.min(2,(int)((y-260)/90)));prefs.edit().putInt(keys[i],Math.min(100,prefs.getInt(keys[i],100)-10)).apply();invalidate();}
    }
  }
}
