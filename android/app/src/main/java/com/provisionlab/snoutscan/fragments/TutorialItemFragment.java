package com.provisionlab.snoutscan.fragments;

import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.provisionlab.snoutscan.R;

import de.hdodenhof.circleimageview.CircleImageView;

public class TutorialItemFragment extends Fragment {

    public static final String DRAWABLE_ID = "drawable_id";
    public static final String TEXT = "text";

    public TutorialItemFragment() {
    }

    public static TutorialItemFragment newInstance(int drawableId, String text) {

        Bundle args = new Bundle();
        args.putInt(DRAWABLE_ID, drawableId);
        args.putString(TEXT, text);

        TutorialItemFragment fragment = new TutorialItemFragment();
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.tutorial_item_layout, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        CircleImageView tutImageView = view.findViewById(R.id.image);
        tutImageView.setImageResource(getArguments().getInt(DRAWABLE_ID));

        TextView tutTextView = view.findViewById(R.id.text);
        tutTextView.setText(getArguments().getString(TEXT));
    }
}
