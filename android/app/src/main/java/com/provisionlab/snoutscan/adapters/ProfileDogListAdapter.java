package com.provisionlab.snoutscan.adapters;

import android.content.Context;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.DiskCacheStrategy;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.models.DogItem;
import com.provisionlab.snoutscan.utilities.Utils;

import java.util.ArrayList;

import butterknife.BindView;
import butterknife.ButterKnife;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class ProfileDogListAdapter extends RecyclerView.Adapter<ProfileDogListAdapter.ViewHolder> {

    private Context context;
    private final ArrayList<DogItem> dogsItems;
    private OnDogClickListener onClickListener;

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
        holder.bind(dogsItems.get(position));
    }

    @Override
    public int getItemCount() {
        return dogsItems.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        @BindView(R.id.iv_dog_profile)
        ImageView dogImageView;
        @BindView(R.id.txt_dog_name)
        TextView dogName;
        @BindView(R.id.txt_breed)
        TextView dogBreed;
        @BindView(R.id.txt_dog_sex)
        TextView dogSex;
        @BindView(R.id.txt_dog_age)
        TextView dogAge;
        @BindView(R.id.txt_dog_location)
        TextView dogLocation;

        ViewHolder(View itemView) {
            super(itemView);
            ButterKnife.bind(this, itemView);
        }

        public void bind(DogItem dogItem) {
            dogName.setText(dogItem.getName());
            dogBreed.setText(dogItem.getBreed());
            dogSex.setText(dogItem.getSex());
            dogAge.setText(Utils.getAge(dogItem));
            dogLocation.setText(dogItem.getLocation());

            itemView.setOnClickListener(view -> {
                if (onClickListener != null) {
                    onClickListener.onClick(dogItem);
                }
            });

            Glide.with(dogImageView.getContext())
                    .load(Utils.getUrl(dogItem))
                    .skipMemoryCache(true)
                    .diskCacheStrategy(DiskCacheStrategy.NONE)
                    .into(dogImageView);
        }
    }

    public void setListener(OnDogClickListener listener) {
        onClickListener = listener;
    }


    public interface OnDogClickListener {
        void onClick(DogItem dogItem);
    }
}
