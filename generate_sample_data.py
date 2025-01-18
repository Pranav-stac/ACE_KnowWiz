import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

def generate_campaign_data(num_days=90):
    """Generate realistic campaign data with more variance in distribution"""
    
    np.random.seed(42)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Platforms with dynamic weights that change over time
    platforms = {
        'Instagram': {'base_weight': 0.3, 'trend': 0.001},  # Growing platform
        'Facebook': {'base_weight': 0.25, 'trend': -0.0005},  # Slightly declining
        'LinkedIn': {'base_weight': 0.2, 'trend': 0.0008},   # Growing for B2B
        'Twitter': {'base_weight': 0.15, 'trend': -0.001},   # Declining
        'TikTok': {'base_weight': 0.1, 'trend': 0.002}      # Rapidly growing
    }
    
    # Campaign types with platform-specific effectiveness
    campaign_types = {
        'Brand Awareness': {
            'Instagram': {'weight': 0.4, 'impression_mult': 2.5, 'engagement_rate': 0.04},
            'Facebook': {'weight': 0.3, 'impression_mult': 2.0, 'engagement_rate': 0.03},
            'LinkedIn': {'weight': 0.2, 'impression_mult': 1.5, 'engagement_rate': 0.02},
            'Twitter': {'weight': 0.3, 'impression_mult': 1.8, 'engagement_rate': 0.025},
            'TikTok': {'weight': 0.5, 'impression_mult': 3.0, 'engagement_rate': 0.05}
        },
        'Lead Generation': {
            'Instagram': {'weight': 0.2, 'impression_mult': 1.0, 'engagement_rate': 0.03},
            'Facebook': {'weight': 0.3, 'impression_mult': 1.2, 'engagement_rate': 0.04},
            'LinkedIn': {'weight': 0.4, 'impression_mult': 1.5, 'engagement_rate': 0.05},
            'Twitter': {'weight': 0.2, 'impression_mult': 0.8, 'engagement_rate': 0.02},
            'TikTok': {'weight': 0.1, 'impression_mult': 0.7, 'engagement_rate': 0.02}
        },
        'Sales': {
            'Instagram': {'weight': 0.3, 'impression_mult': 1.8, 'engagement_rate': 0.035},
            'Facebook': {'weight': 0.35, 'impression_mult': 2.0, 'engagement_rate': 0.04},
            'LinkedIn': {'weight': 0.3, 'impression_mult': 1.6, 'engagement_rate': 0.03},
            'Twitter': {'weight': 0.2, 'impression_mult': 1.2, 'engagement_rate': 0.025},
            'TikTok': {'weight': 0.3, 'impression_mult': 1.5, 'engagement_rate': 0.045}
        },
        'Content Promotion': {
            'Instagram': {'weight': 0.35, 'impression_mult': 1.5, 'engagement_rate': 0.06},
            'Facebook': {'weight': 0.25, 'impression_mult': 1.3, 'engagement_rate': 0.05},
            'LinkedIn': {'weight': 0.3, 'impression_mult': 1.4, 'engagement_rate': 0.04},
            'Twitter': {'weight': 0.4, 'impression_mult': 1.6, 'engagement_rate': 0.055},
            'TikTok': {'weight': 0.4, 'impression_mult': 1.8, 'engagement_rate': 0.07}
        }
    }
    
    data = []
    for i, date in enumerate(dates):
        # Calculate evolving platform weights
        day_progress = i / len(dates)
        current_platform_weights = {
            platform: max(0.05, min(0.5, info['base_weight'] + (info['trend'] * i)))
            for platform, info in platforms.items()
        }
        
        # Normalize weights
        weight_sum = sum(current_platform_weights.values())
        current_platform_weights = {
            k: v/weight_sum for k, v in current_platform_weights.items()
        }
        
        # Add seasonal effects
        season_multiplier = 1.0 + 0.3 * np.sin(2 * np.pi * date.dayofweek / 7)  # Weekly pattern
        holiday_multiplier = 1.0 + 0.5 * np.sin(2 * np.pi * date.day / 365)     # Yearly pattern
        
        for platform in platforms.keys():
            # Dynamic number of campaigns based on platform popularity
            base_campaigns = np.random.poisson(
                max(1, 5 * current_platform_weights[platform])
            )
            
            for _ in range(base_campaigns):
                # Weight campaign types by platform
                campaign_weights = [
                    types[platform]['weight'] 
                    for types in campaign_types.values()
                ]
                campaign_type = np.random.choice(
                    list(campaign_types.keys()),
                    p=np.array(campaign_weights) / sum(campaign_weights)
                )
                
                # Get platform-specific metrics
                metrics = campaign_types[campaign_type][platform]
                
                # Generate base metrics with more variance
                base_impressions = np.random.gamma(
                    10000 * metrics['impression_mult'],
                    0.5
                ) * season_multiplier * holiday_multiplier
                
                # Add random spikes and dips
                if np.random.random() < 0.1:  # 10% chance of exceptional performance
                    base_impressions *= np.random.choice([0.2, 0.5, 2.0, 5.0])
                
                impressions = max(100, int(base_impressions))
                
                # Much higher conversion rates for better funnel visibility
                engagement_rate = np.random.uniform(0.15, 0.25)  # 15-25% engagement
                engagement = int(impressions * engagement_rate)
                
                click_rate = np.random.uniform(0.25, 0.35)  # 25-35% of engaged users click
                clicks = int(engagement * click_rate)
                
                conversion_rate = np.random.uniform(0.15, 0.25)  # 15-25% of clicks convert
                conversions = int(clicks * conversion_rate)
                
                # Ensure minimum values and logical progression
                engagement = max(int(impressions * 0.15), min(engagement, impressions))
                clicks = max(int(engagement * 0.25), min(clicks, engagement))
                conversions = max(int(clicks * 0.15), min(conversions, clicks))
                
                # Variable cost per platform and campaign type
                base_cpm = np.random.normal(
                    5 * metrics['impression_mult'],
                    metrics['impression_mult']
                )
                cost = round(impressions * base_cpm / 1000, 2)
                
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'platform': platform,
                    'campaign_type': campaign_type,
                    'impressions': impressions,
                    'engagement': engagement,
                    'clicks': clicks,
                    'conversions': conversions,
                    'cost': cost,
                    'ctr': round(clicks/impressions*100, 3) if impressions > 0 else 0,
                    'conversion_rate': round(conversions/clicks*100, 3) if clicks > 0 else 0,
                    'cpc': round(cost/clicks, 2) if clicks > 0 else 0,
                    'roas': round((conversions * 50)/cost, 2) if cost > 0 else 0
                })
    
    return pd.DataFrame(data)

def save_sample_data(df, output_dir='sample_data'):
    """Save the sample data in multiple formats"""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as CSV
    df.to_csv(f'{output_dir}/campaign_data.csv', index=False)
    
    # Save as Excel with multiple sheets
    with pd.ExcelWriter(f'{output_dir}/campaign_data.xlsx') as writer:
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        
        # Add platform summary sheet
        platform_summary = df.groupby('platform').agg({
            'impressions': 'sum',
            'engagement': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'cost': 'sum',
            'ctr': 'mean',
            'conversion_rate': 'mean',
            'roas': 'mean'
        }).round(2)
        platform_summary.to_excel(writer, sheet_name='Platform Summary')
        
        # Add daily summary sheet
        daily_summary = df.groupby('date').agg({
            'impressions': 'sum',
            'engagement': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'cost': 'sum'
        }).round(2)
        daily_summary.to_excel(writer, sheet_name='Daily Summary')
    
    # Save as JSON
    df.to_json(f'{output_dir}/campaign_data.json', orient='records', date_format='iso')

if __name__ == "__main__":
    # Generate sample data
    print("Generating sample campaign data...")
    df = generate_campaign_data(90)  # 90 days of data
    
    # Save in multiple formats
    print("Saving data in multiple formats...")
    save_sample_data(df)
    
    print(f"Generated {len(df)} records of campaign data")
    print("\nSample data statistics:")
    print("\nTotal by platform:")
    print(df.groupby('platform')['impressions'].sum().sort_values(ascending=False))
    print("\nAverage metrics:")
    print(df[['impressions', 'engagement', 'clicks', 'conversions', 'cost']].mean().round(2)) 