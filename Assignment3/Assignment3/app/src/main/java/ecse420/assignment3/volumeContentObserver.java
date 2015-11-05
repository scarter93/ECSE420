package ecse420.assignment3;

import android.app.Service;
import android.content.Context;
import android.database.ContentObserver;
import android.media.AudioManager;
import android.os.Handler;
import android.util.Log;
import android.widget.Toast;
//class for observing volume
public class volumeContentObserver extends ContentObserver {
    Service service;
    private int prevVol = 0;
    //constructor
    public volumeContentObserver(Handler handler, Service service) {
        super(handler);
        this.service = service;
    }
    @Override
    public boolean deliverSelfNotifications(){
        return super.deliverSelfNotifications();
    }

    //onChange: get new volume and toast notify
    @Override
    public void onChange(boolean selfChange) {
        super.onChange(selfChange);
        AudioManager volumeCheck = (AudioManager) this.service.getApplicationContext().getSystemService(Context.AUDIO_SERVICE);
        int currentVolume = volumeCheck.getStreamVolume(AudioManager.STREAM_RING);
        Log.w("myApp", "no network");
        Toast.makeText(this.service.getApplicationContext(), "Change in volume detected, Volume: " + currentVolume, Toast.LENGTH_LONG).show();

    }

}
