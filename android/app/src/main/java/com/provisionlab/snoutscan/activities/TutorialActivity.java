package com.provisionlab.snoutscan.activities;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.TabLayout;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.LinearLayout;

import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.adapters.TutorialPagerAdapter;
import com.provisionlab.snoutscan.utilities.SharedPrefsUtil;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;

public class TutorialActivity extends AppCompatActivity {

    @BindView(R.id.tutorial)
    ViewPager tutorialViewPager;
    @BindView(R.id.controls_layout)
    LinearLayout controlsLayout;

    public static final String FIRST_RUN = "firstRun";
    private TutorialPagerAdapter tutorialPagerAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tutorial);
        ButterKnife.bind(this);

        initUI();
    }

    private void initUI() {
        tutorialViewPager = findViewById(R.id.tutorial);
        tutorialPagerAdapter = new TutorialPagerAdapter(this, getSupportFragmentManager());
        tutorialViewPager.setAdapter(tutorialPagerAdapter);

        TabLayout tabLayout = findViewById(R.id.tab_layout);
        tabLayout.setupWithViewPager(tutorialViewPager, true);

        tutorialViewPager.addOnPageChangeListener(new ViewPager.OnPageChangeListener() {

            @Override
            public void onPageScrolled(int position, float positionOffset, int positionOffsetPixels) {
            }

            @Override
            public void onPageSelected(int position) {
                switch (position) {
                    case 0:
                    case 1:
                        controlsLayout.setVisibility(View.VISIBLE);
                        break;
                    case 2:
                        controlsLayout.setVisibility(View.GONE);
                        break;
                }
            }

            @Override
            public void onPageScrollStateChanged(int state) {
            }
        });
    }

    @OnClick({R.id.next, R.id.skip, R.id.lets_go})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.next:
                if (tutorialViewPager.getCurrentItem() != 2) {
                    tutorialViewPager.setCurrentItem(tutorialViewPager.getCurrentItem() + 1);
                }
                break;
            case R.id.skip:
            case R.id.lets_go:
                Intent intent = new Intent(this, LoginActivity.class);
                startActivity(intent);
                SharedPrefsUtil.putBooleanData(this, FIRST_RUN, true);
                finish();
                break;

        }
    }
}
