package ecse420.assignment3;

import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.widget.Toast;


public class AssignmentService extends Service {

    public AssignmentService() {
    }
    //onCreate: calls super onCreate and uses a toast notification
    @Override
    public void onCreate() {
        super.onCreate();
        Toast.makeText(this, "service created", Toast.LENGTH_LONG).show();
    }
    @Override
    public IBinder onBind(Intent intent){
        throw new UnsupportedOperationException("Not Implemented yet");
    }
    //onDestroy: toast notification and calls super.onDestroy
    @Override
    public void onDestroy() {
        Toast.makeText(this, "service destroyed", Toast.LENGTH_LONG).show();
        super.onDestroy();
    }
    //onStartCommand: toast and start volumeContentObserver
    @Override
    public int onStartCommand(Intent intent, int flags, int startID){
        Toast.makeText(this, "service started", Toast.LENGTH_LONG).show();
        //Toast.makeText(this, "service stopping", Toast.LENGTH_SHORT).show();
        volumeContentObserver volumeObserver = new volumeContentObserver( new Handler(), this);

        this.getApplicationContext().getContentResolver().registerContentObserver(
                android.provider.Settings.System.CONTENT_URI, true,
                volumeObserver);
        return Service.START_STICKY;
    }

}
