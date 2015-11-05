package ecse420.assignment3;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Date;

public class LifeCycle0858 extends AppCompatActivity {
    ArrayList<String> newlist  = new ArrayList<String>();

    //super create and start service, update ListView
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_my);
        Intent intent = new Intent(this, AssignmentService.class);
        this.startService(intent);
        String type = "onCreate";
        addItem(type);
    }
    //add ListView and call super
    @Override
    protected void onPause(){
        String type = "onPause";
        addItem(type);
        super.onPause();
    }

    //call super and add to ListView
    @Override
    protected void onResume() {
        super.onResume();
        String type = "onResume";
        addItem(type);
    }
    //call super and add item to ListView
    @Override
    protected void onStart() {
        super.onStart();
        String type = "onStart";
        addItem(type);

    }
    //add item to ListView and call super
    @Override
    protected void onStop() {
        String type = "onStop";
        addItem(type);
        super.onStop();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_my, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
    //toast and call super
    @Override
    public void onDestroy() {
        Toast.makeText(this , "onDestroy" , Toast.LENGTH_LONG).show();
        super.onDestroy();  // Always call the superclass

        // Stop method tracing that the activity started during onCreate()
        android.os.Debug.stopMethodTracing();
    }
    //function for button click -- stop service
    public void stopMyService(View view){
        Intent intent = new Intent(this, AssignmentService.class);
        this.stopService(intent);
    }
    //function for adding item to ListView and update view
    private void addItem(String type) {
        String currentDateTime = DateFormat.getDateTimeInstance().format(new Date());
        String entry = type + " " + currentDateTime;
        newlist.add(entry);

        ArrayAdapter<String> itemsAdapter = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, newlist);
        ListView listView = (ListView) findViewById(R.id.listView);
        listView.setAdapter(itemsAdapter);
        listView.invalidateViews();
    }

}
