package org.rexglue.fiberprobe;
import android.app.Activity; import android.os.Bundle; import android.graphics.Typeface; import android.view.Gravity; import android.widget.LinearLayout; import android.widget.TextView; import android.widget.Button;
public final class MainActivity extends Activity {
 static { System.loadLibrary("fiber_test"); } private native String runFiberTest();
 @Override public void onCreate(Bundle state){super.onCreate(state); LinearLayout root=new LinearLayout(this);root.setOrientation(1);root.setPadding(28,48,28,28);root.setGravity(Gravity.CENTER_HORIZONTAL);
 TextView title=new TextView(this);title.setText("ReXGlue • Teste de fibras ARM64");title.setTextSize(22);title.setTypeface(null,Typeface.BOLD);root.addView(title);
 TextView result=new TextView(this);result.setText("Toque em EXECUTAR para testar a troca de contexto no Android.");result.setTextSize(17);result.setPadding(0,36,0,36);root.addView(result);
 Button run=new Button(this);run.setText("EXECUTAR TESTE");run.setOnClickListener(v->{run.setEnabled(false);try{result.setText(runFiberTest());}catch(Throwable e){result.setText("FALHA JNI: "+e);}finally{run.setEnabled(true);}});root.addView(run);
 TextView note=new TextView(this);note.setText("Teste isolado. Não inicia o jogo e não ativa Save/Load.");note.setTextSize(13);note.setPadding(0,36,0,0);root.addView(note);setContentView(root);}
}
