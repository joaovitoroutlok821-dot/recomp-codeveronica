package org.libsdl.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.SharedPreferences;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.graphics.Color;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.LayerDrawable;
import android.graphics.drawable.Drawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

public final class GameSettingsActivity extends Activity {
  private SharedPreferences p;
  private LinearLayout content, tabs, main;
  private int red = Color.rgb(238, 12, 28);
  private int muted = Color.rgb(190, 198, 210);
  private String current = "Gráficos";
  private int dp(float v) { return (int)(v * getResources().getDisplayMetrics().density + 0.5f); }

  @Override public void onCreate(Bundle b) {
    super.onCreate(b);
    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
    getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    p = getSharedPreferences("recvx_settings", MODE_PRIVATE);
    buildUi();
    show(current);
  }

  private GradientDrawable shape(int color, int stroke, int radius) {
    GradientDrawable d = new GradientDrawable();
    d.setCornerRadius(dp(radius));
    if (color == 0xFF97000B) {
      d.setOrientation(GradientDrawable.Orientation.TOP_BOTTOM);
      d.setColors(new int[]{0xFFFF2638,0xFFB50012,0xFF76000A});
    } else if (color == 0xFF17191F) {
      d.setColor(0xF5101117);
    } else {
      d.setColor(color);
    }
    if (stroke != 0) d.setStroke(dp(1.5f), stroke);
    return d;
  }
  private TextView label(String s, int size, int color, boolean bold) {
    TextView t = new TextView(this); t.setText(s); t.setTextSize(size); t.setTextColor(color);
    if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
    return t;
  }
  private Button action(String s, boolean selected) {
    Button b = new Button(this); b.setText(s); b.setTextSize(13); b.setAllCaps(false);
    b.setTextColor(Color.WHITE);
    b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
    b.setBackground(shape(selected ? 0xFF97000B : 0xFF17191F, selected ? 0xFFFF2638 : 0xFFB51A2A, 8));
    b.setElevation(dp(selected ? 7 : 2));
    b.setPadding(dp(8),dp(3),dp(8),dp(3));
    return b;
  }
  private void buildUi() {
    LinearLayout root = new LinearLayout(this);
    root.setOrientation(LinearLayout.VERTICAL);
    int coverId=getResources().getIdentifier("recvx_cover","drawable",getPackageName());
    if(coverId!=0) {
      Drawable art=getResources().getDrawable(coverId);
      Drawable shade=new ColorDrawable(0x99020710);
      root.setBackground(new LayerDrawable(new Drawable[]{art,shade}));
    } else {
      root.setBackgroundColor(Color.rgb(3,5,9));
    }
    root.setPadding(dp(12), dp(8), dp(12), dp(4));

    LinearLayout body = new LinearLayout(this);
    body.setOrientation(LinearLayout.HORIZONTAL);
    root.addView(body, new LinearLayout.LayoutParams(-1, 0, 1));

    LinearLayout side = new LinearLayout(this);
    side.setOrientation(LinearLayout.VERTICAL);
    side.setPadding(dp(8), dp(8), dp(8), dp(8));
    side.setBackground(shape(0xD9080A0F, 0xFFFF2638, 12));
    side.setElevation(dp(8));
    TextView game = label("RESIDENT EVIL\nCODE: VERONICA X HD", 17, Color.WHITE, true);
    game.setGravity(Gravity.CENTER);
    game.setPadding(dp(4), dp(8), dp(4), dp(14));
    side.addView(game, new LinearLayout.LayoutParams(-1, dp(92)));
    String[] menu = {"▷  Iniciar Jogo", "⚙  Configurações", "♧  Controles", "▣  Salvar / Carregar", "ⓘ  Informações", "⏻  Sair"};
    for (int i=0;i<menu.length;i++) {
      final int item=i;
      Button b=action(menu[i], i==1);
      LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(-1, dp(48));
      bp.bottomMargin=dp(7); side.addView(b,bp);
      b.setOnClickListener(v -> {
        if(item==0) { finish(); }
        else if(item==1) { current="Gráficos"; refreshTabs(); show(current); }
        else if(item==2) { current="Controles"; refreshTabs(); show(current); }
        else if(item==3) Toast.makeText(this,"Salvar/carregar ainda não está integrado ao runtime.",Toast.LENGTH_SHORT).show();
        else if(item==4) new android.app.AlertDialog.Builder(this).setTitle("Informações").setMessage("Resident Evil Code: Veronica X HD — edição dublada para Android ARM64.").setPositiveButton("OK",null).show();
        else finish();
      });
    }
    TextView edition=label("EDIÇÃO DUBLADA • ANDROID",11,muted,false);
    edition.setGravity(Gravity.CENTER); edition.setPadding(0,dp(8),0,0); side.addView(edition);
    body.addView(side,new LinearLayout.LayoutParams(dp(205),-1));

    main=new LinearLayout(this); main.setOrientation(LinearLayout.VERTICAL);
    LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(0,-1,1); mp.leftMargin=dp(10); body.addView(main,mp);
    TextView title=label("Configurações",24,Color.WHITE,true);
    title.setPadding(dp(4),0,0,dp(5)); main.addView(title);

    tabs=new LinearLayout(this); tabs.setOrientation(LinearLayout.HORIZONTAL);
    String[] names={"▣  Gráficos","◉  Desempenho","♧  Controles","◖  Áudio"};
    String[] keys={"Gráficos","Desempenho","Controles","Áudio"};
    for(int i=0;i<keys.length;i++){
      final String key=keys[i]; Button b=action(names[i],key.equals(current));
      LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,dp(42),1); tp.setMargins(dp(3),dp(2),dp(3),dp(6));
      tabs.addView(b,tp); b.setOnClickListener(v->{current=key;refreshTabs();show(key);});
    }
    main.addView(tabs);
    ScrollView scroll=new ScrollView(this); scroll.setFillViewport(true);
    content=new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL);
    content.setPadding(dp(7),dp(5),dp(7),dp(5));
    scroll.addView(content); main.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));

    LinearLayout footer=new LinearLayout(this); footer.setOrientation(LinearLayout.HORIZONTAL);
    Button reset=action("↶  Restaurar padrões",false);
    reset.setOnClickListener(v->{p.edit().clear().apply();current="Gráficos";refreshTabs();show(current);});
    Button apply=action("✓  Aplicar",true);
    apply.setOnClickListener(v->{p.edit().apply();Toast.makeText(this,"Configurações salvas.",Toast.LENGTH_SHORT).show();finish();});
    LinearLayout.LayoutParams fp=new LinearLayout.LayoutParams(0,dp(42),1); fp.setMargins(dp(4),dp(5),dp(4),dp(2));
    footer.addView(reset,fp); footer.addView(apply,fp); main.addView(footer);
    TextView status=label("▱  Diretório do jogo: consulte a tela inicial     •     ♧ Controle: estado detectado pelo Android     •     Controles na tela: configurável     •     Versão: v1.0.0",11,muted,false);
    status.setGravity(Gravity.CENTER_VERTICAL); status.setPadding(dp(8),dp(7),dp(8),dp(7));
    status.setBackground(shape(0xFF080A0E,0xFF6E1B25,5));
    root.addView(status,new LinearLayout.LayoutParams(-1,dp(34)));
    setContentView(root);
  }
  private void refreshTabs() {
    String[] keys={"Gráficos","Desempenho","Controles","Áudio"};
    for(int i=0;i<tabs.getChildCount();i++){
      Button b=(Button)tabs.getChildAt(i);
      b.setBackground(shape(keys[i].equals(current)?0xFF97000B:0xFF17191F,keys[i].equals(current)?0xFFFF2638:0xFFB51A2A,8));
      b.setElevation(dp(keys[i].equals(current)?7:2));
    }
  }
  private LinearLayout panel(String heading) {
    LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL);
    box.setPadding(dp(13),dp(10),dp(13),dp(10)); box.setBackground(shape(0xE5090B10,0xFFFF1B30,10));
    TextView h=label(heading,19,Color.WHITE,true); h.setPadding(dp(2),dp(1),dp(2),dp(5)); box.addView(h); return box;
  }
  private void row(LinearLayout box,String name,View control) {
    LinearLayout line=new LinearLayout(this); line.setGravity(Gravity.CENTER_VERTICAL);
    TextView l=label(name,14,Color.WHITE,false); line.addView(l,new LinearLayout.LayoutParams(0,dp(30),1));
    if(control!=null) {
      LinearLayout.LayoutParams controlParams;
      if (control instanceof Switch) {
        controlParams = new LinearLayout.LayoutParams(dp(64), dp(30));
        controlParams.gravity = Gravity.RIGHT | Gravity.CENTER_VERTICAL;
      } else {
        controlParams = new LinearLayout.LayoutParams(dp(190), dp(32));
      }
      line.addView(control, controlParams);
    }
    LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,-2); rp.bottomMargin=dp(2); box.addView(line,rp);
  }
  private void note(LinearLayout box,String s) {
    TextView t=label(s,12,muted,false); t.setPadding(dp(4),dp(4),dp(4),dp(6)); box.addView(t);
  }
  private Spinner choice(String[] values,String key,int def) {
    Spinner s=new Spinner(this);
    ArrayAdapter<String>a=new ArrayAdapter<String>(this,android.R.layout.simple_spinner_item,values) {
      @Override public View getView(int position, View convertView, android.view.ViewGroup parent) {
        TextView t=(TextView)super.getView(position,convertView,parent);
        t.setTextColor(Color.WHITE); t.setTextSize(13); t.setGravity(Gravity.CENTER_VERTICAL);
        t.setPadding(dp(8),0,dp(4),0); return t;
      }
      @Override public View getDropDownView(int position, View convertView, android.view.ViewGroup parent) {
        TextView t=(TextView)super.getDropDownView(position,convertView,parent);
        t.setTextColor(Color.WHITE); t.setTextSize(14); t.setGravity(Gravity.CENTER_VERTICAL);
        t.setPadding(dp(12),dp(10),dp(8),dp(10));
        t.setBackgroundColor(0xFF202126); return t;
      }
    };
    a.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item); s.setAdapter(a);
    s.setBackground(shape(0xFF202126,0xFF8E2932,6)); s.setSelection(p.getInt(key,def));
    s.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
      public void onNothingSelected(android.widget.AdapterView<?>x){}
      public void onItemSelected(android.widget.AdapterView<?>x,View v,int pos,long id){p.edit().putInt(key,pos).apply();}
    }); return s;
  }
  private Switch toggle(String title,String key,boolean def) {
    Switch s=new Switch(this);
    s.setText("");
    s.setShowText(false);
    s.setMinimumWidth(dp(60));
    s.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
    int[][] states = new int[][] {
      new int[] { android.R.attr.state_checked },
      new int[] {}
    };
    int[] thumbColors = new int[] { 0xFFFFFFFF, 0xFFE4E6EA };
    int[] trackColors = new int[] { 0xFFE50920, 0xFF555A63 };
    s.setThumbTintList(new ColorStateList(states, thumbColors));
    s.setTrackTintList(new ColorStateList(states, trackColors));
    s.setChecked(p.getBoolean(key,def));
    s.setOnCheckedChangeListener((v,on)->p.edit().putBoolean(key,on).apply());
    return s;
  }
  private SeekBar slider(String key,int def) {
    SeekBar s=new SeekBar(this); s.setMax(100); s.setProgress(p.getInt(key,def));
    s.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
      public void onProgressChanged(SeekBar b,int v,boolean user){if(user)p.edit().putInt(key,v).apply();}
      public void onStartTrackingTouch(SeekBar b){} public void onStopTrackingTouch(SeekBar b){}
    }); return s;
  }
  private void show(String tab) {
    content.removeAllViews();
    if(tab.equals("Gráficos")) {
      LinearLayout split=new LinearLayout(this); split.setOrientation(LinearLayout.HORIZONTAL);
      LinearLayout g=panel("Gráficos"), q=panel("Qualidade de imagem");
      row(g,"Resolução de saída",choice(new String[]{"720p (1280×720)","1080p (1920×1080)"}, "resolution",1));
      row(g,"Escala de renderização",choice(new String[]{"100% (Nativa)"}, "render_scale",0));
      row(g,"Qualidade de imagem",choice(new String[]{"Alta","Média","Baixa"}, "image_quality",0));
      row(g,"Filtro de imagem",choice(new String[]{"Bilinear"}, "image_filter",0));
      row(g,"Filtro FSR",choice(new String[]{"Desativado","FSR (FidelityFX)"}, "fsr",0));
      row(g,"Modo FSR",choice(new String[]{"Quality","Balanced","Performance"}, "fsr_mode",0));
      row(g,"Nitidez (CAS)",slider("cas_sharpness",70));
      row(g,"Anti-aliasing (AA)",choice(new String[]{"Desativado","Ativado"}, "anti_aliasing",0));
      row(g,"Efeitos de partículas",choice(new String[]{"Alto","Médio","Baixo"}, "particles",0));
      row(g,"Proporção da tela",choice(new String[]{"Automática (16:9)","4:3","16:9","16:10"}, "aspect_ratio",0));
      note(q,"As opções de qualidade, FSR, CAS, anti-aliasing, partículas e proporção serão aplicadas somente quando o runtime oferecer suporte real.");
      note(q,"Filtro bilinear e resolução são as opções atualmente expostas pelo renderer Android.");
      LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,-2,1); cp.setMargins(dp(3),dp(3),dp(3),dp(3));
      LinearLayout.LayoutParams gp=new LinearLayout.LayoutParams(0,-2,2.05f); gp.setMargins(dp(3),dp(3),dp(5),dp(3));
      LinearLayout.LayoutParams qp=new LinearLayout.LayoutParams(0,-2,1.0f); qp.setMargins(dp(5),dp(3),dp(3),dp(3));
      g.setElevation(dp(5)); q.setElevation(dp(5));
      split.addView(g,gp); split.addView(q,qp); content.addView(split);
    } else if(tab.equals("Desempenho")) {
      LinearLayout split=new LinearLayout(this); split.setOrientation(LinearLayout.HORIZONTAL);
      LinearLayout perf=panel("Desempenho"), info=panel("Informações");
      row(perf,"Limite de FPS",choice(new String[]{"30 FPS","60 FPS","120 FPS","Ilimitado"},"fps_limit",1));
      row(perf,"Sincronização vertical (V-Sync)",toggle("Ativado","vsync",true));
      row(perf,"Contador de FPS",toggle("Exibir FPS","show_fps",true));
      row(perf,"Cache de shaders",toggle("Ativado","shader_cache",true));
      row(perf,"Reduzir efeitos pesados",toggle("Ativado","reduce_effects",false));
      note(info,"O contador apresenta a taxa de apresentação medida pelo renderer.");
      note(info,"Limite de FPS, V-Sync, cache e redução de efeitos ainda precisam de integração e validação no runtime antes de produzirem efeito no jogo.");
      LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,-2,1); cp.setMargins(dp(3),dp(3),dp(3),dp(3));
      LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(0,-2,1.55f); pp.setMargins(dp(3),dp(3),dp(5),dp(3));
      LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(0,-2,1.0f); ip.setMargins(dp(5),dp(3),dp(3),dp(3));
      perf.setElevation(dp(5)); info.setElevation(dp(5));
      split.addView(perf,pp); split.addView(info,ip); content.addView(split);
    } else if(tab.equals("Controles")) {
      LinearLayout controls=panel("Controles");
      row(controls,"Controles na tela",choice(new String[]{"Automático","Sempre mostrar","Sempre ocultar"},"touch_mode",0));
      Button edit=action("↔  Editar posição dos controles",true);
      edit.setOnClickListener(v->startActivity(new Intent(this,TouchLayoutEditorActivity.class)));
      controls.addView(edit,new LinearLayout.LayoutParams(-1,dp(42)));
      note(controls,"O editor permite arrastar o joystick e os botões. Ajustes de tamanho e transparência ainda não estão disponíveis.");
      note(controls,"O modo automático deve ocultar os controles após entrada física confirmada e mostrá-los novamente quando o controle for desconectado. Validar no aparelho.");
      content.addView(controls);
    } else {
      LinearLayout audio=panel("Áudio");
      row(audio,"Volume geral",slider("audio_master",100));
      row(audio,"Volume da música",slider("audio_music",100));
      row(audio,"Volume dos efeitos",slider("audio_sfx",100));
      note(audio,"Os controles de volume são armazenados, mas ainda não estão conectados ao mixer do runtime.");
      content.addView(audio);
    }
  }
}
