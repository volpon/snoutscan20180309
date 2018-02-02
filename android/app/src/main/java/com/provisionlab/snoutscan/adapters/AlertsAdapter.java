package com.provisionlab.snoutscan.adapters;

import android.content.Context;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;

import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.models.Alert;

import java.util.ArrayList;

/**
 * Created by Evgeniy on 22-Jan-18.
 */

public class AlertsAdapter extends RecyclerView.Adapter<AlertsAdapter.ViewHolder> {

    private Context context;
    private ArrayList<Alert> alerts;

    public AlertsAdapter(Context context, ArrayList<Alert> alerts) {
        this.context = context;
        this.alerts = alerts;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.alerts_list_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        Alert alert = alerts.get(position);
    }

    @Override
    public int getItemCount() {
        return 0;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        ImageView dogImageView;
        ImageView frameImageView;
        TextView dogStatusTextView;
        TextView dogBreed;
        TextView dogSex;
        LinearLayout contactLayout;
        RelativeLayout contactByPhone;
        RelativeLayout contactByMessaging;

        ViewHolder(View itemView) {
            super(itemView);
            dogImageView = itemView.findViewById(R.id.dog_photo);
            frameImageView = itemView.findViewById(R.id.frame);
            dogStatusTextView = itemView.findViewById(R.id.dog_status);
            dogBreed = itemView.findViewById(R.id.breed);
            dogSex = itemView.findViewById(R.id.sex);
            contactLayout = itemView.findViewById(R.id.contact_layout);
            contactByPhone = itemView.findViewById(R.id.contact_by_phone);
            contactByMessaging = itemView.findViewById(R.id.contact_by_messaging);
        }
    }
}
