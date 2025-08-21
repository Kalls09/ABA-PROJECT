import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LoginScreen from './src/screens/LoginScreen';
import PatientsScreen from './src/screens/PatientsScreen';

export type RootStackParamList = {
  Login: undefined;
  Patients: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Patients" component={PatientsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
