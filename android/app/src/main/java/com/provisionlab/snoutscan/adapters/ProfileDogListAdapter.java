package com.provisionlab.snoutscan.adapters;

import android.content.Context;
import android.content.Intent;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.DiskCacheStrategy;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.activities.DogDetailActivity;
import com.provisionlab.snoutscan.models.DogItem;
import com.provisionlab.snoutscan.utilities.Utils;

import java.util.ArrayList;

import static com.provisionlab.snoutscan.activities.DogDetailActivity.DOG_DATA;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class ProfileDogListAdapter extends RecyclerView.Adapter<ProfileDogListAdapter.ViewHolder> {

    private Context context;
    private final ArrayList<DogItem> dogsItems;

    public ProfileDogListAdapter(Context context, ArrayList<DogItem> dogsItems) {
        this.context = context;
        this.dogsItems = dogsItems;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_profile_dog, parent, false);

        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        DogItem dogItem = dogsItems.get(position);
        holder.dogName.setText(dogItem.getName());
        holder.dogBreed.setText(dogItem.getBreed());
        holder.dogSex.setText(dogItem.getSex());
        holder.dogAge.setText(Utils.getAge(dogItem));
        holder.dogLocation.setText(dogItem.getLocation());

        holder.itemView.setOnClickListener(view -> {
            Intent intent = new Intent(context, DogDetailActivity.class);
            intent.putExtra(DOG_DATA, dogItem);
            context.startActivity(intent);
        });

        Glide.with(holder.dogImageView.getContext())
                .load(Utils.getUrl(dogItem))
                .skipMemoryCache(true)
                .diskCacheStrategy(DiskCacheStrategy.NONE)
                .into(holder.dogImageView);
    }

    @Override
    public int getItemCount() {
        return dogsItems.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        ImageView dogImageView;
        TextView dogName;
        TextView dogBreed;
        TextView dogSex;
        TextView dogAge;
        TextView dogLocation;

        ViewHolder(View itemView) {
            super(itemView);
            dogImageView = itemView.findViewById(R.id.iv_dog_profile);
            dogName = itemView.findViewById(R.id.txt_dog_name);
            dogBreed = itemView.findViewById(R.id.txt_breed);
            dogSex = itemView.findViewById(R.id.txt_dog_sex);
            dogAge = itemView.findViewById(R.id.txt_dog_age);
            dogLocation = itemView.findViewById(R.id.txt_dog_location);
        }
    }
}
