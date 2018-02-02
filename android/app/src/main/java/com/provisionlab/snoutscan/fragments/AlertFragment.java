package com.provisionlab.snoutscan.fragments;

import android.app.Fragment;
import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.activities.RegisterDogActivity;
import com.provisionlab.snoutscan.adapters.AlertsAdapter;
import com.provisionlab.snoutscan.models.Alert;

import java.util.ArrayList;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class AlertFragment extends Fragment {

    private ArrayList<Alert> alerts;
    private AlertsAdapter alertsAdapter;

    @BindView(R.id.dog_list)
    RecyclerView mRecyclerView;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_alert, container, false);
        ButterKnife.bind(this, view);

        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        initUI();
    }

    public void initUI() {
        alertsAdapter = new AlertsAdapter(getActivity(), alerts);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getActivity());
        mRecyclerView.setLayoutManager(linearLayoutManager);
        mRecyclerView.setAdapter(alertsAdapter);
    }

    @OnClick({R.id.btn_add})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btn_add:
                startActivity(new Intent(getActivity(), RegisterDogActivity.class));
                break;
        }
    }
}
